#!/usr/bin/env python3
"""advice-debugger ledger: advice -> experiment -> outcome, persisted.

Storage: $ADVICE_LEDGER_DIR, or ~/.advice-ledger/ by default
  ledger.json  source of truth (a .bak copy is taken before every write)
  ledger.md    human-readable view, regenerated on every write

Commands:
  add --file F             record a new piece of advice (JSON)
  result ID --file F       record the outcome (JSON); closed entries need --force
  postpone ID --to DATE    move the check-in date
  delete ID                remove an entry the user did not want recorded
  due [--all] [--count]    open entries whose check-in date has arrived (or all)
  due --hook               one-line session-start reminder; silent when nothing is due
  search TERM... [--domain D]
  lessons [--domain D]     lessons and broken assumptions from closed entries
  show ID
  stats
  render                   regenerate ledger.md
Pass '-' instead of a file to read JSON from stdin.

Standard library only. Python 3.9+.
"""
import argparse
import datetime as dt
import json
import os
import sys
import time
import unicodedata
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

STATUSES = ("worked", "partial", "failed", "abandoned", "inconclusive")
NEEDS_LESSON = {"partial", "failed", "abandoned"}
VERDICTS = ("held", "broke", "untested")


def ledger_dir(create: bool = True) -> Path:
    d = os.environ.get("ADVICE_LEDGER_DIR")
    p = Path(d).expanduser() if d else Path.home() / ".advice-ledger"
    if create:
        p.mkdir(parents=True, exist_ok=True)
    return p


def today() -> str:
    override = os.environ.get("ADVICE_LEDGER_TODAY")  # for tests
    return override or dt.date.today().isoformat()


def die(msg: str, code: int = 2):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def parse_date(s, field: str) -> str:
    try:
        return dt.date.fromisoformat(str(s)).isoformat()
    except ValueError:
        die(f"{field} must be YYYY-MM-DD, got {s!r}")


class Lock:
    """Cross-platform exclusive lock via O_EXCL; stale after 60 s."""

    def __init__(self, path: Path):
        self.path = path

    def __enter__(self):
        for _ in range(100):
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > 60:
                        self.path.unlink()
                        continue
                except FileNotFoundError:
                    continue
                time.sleep(0.1)
        die("could not acquire ledger lock (another session may be writing)")

    def __exit__(self, *exc):
        os.close(self.fd)
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


def lock() -> Lock:
    return Lock(ledger_dir() / ".lock")


def load() -> dict:
    f = ledger_dir() / "ledger.json"
    if not f.exists():
        return {"version": 1, "entries": []}
    try:
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
            raise ValueError("expected an object with an 'entries' list")
        return data
    except (json.JSONDecodeError, ValueError) as e:
        die(f"{f} is corrupt ({e}). Previous version: {f.parent / 'ledger.json.bak'}. "
            "Ask the user before overwriting anything.")


def save(data: dict):
    d = ledger_dir()
    f = d / "ledger.json"
    if f.exists():
        (d / "ledger.json.bak").write_bytes(f.read_bytes())
    tmp = d / "ledger.json.tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, f)
    (d / "ledger.md").write_text(render_md(data), encoding="utf-8")


def read_json_arg(src: str) -> dict:
    try:
        if src == "-":
            data = json.loads(sys.stdin.buffer.read().decode("utf-8-sig"))
        else:
            with open(src, encoding="utf-8-sig") as fh:
                data = json.load(fh)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as e:
        die(f"could not read JSON ({src}): {e}")
    if not isinstance(data, dict):
        die("JSON root must be an object ({...})")
    return data


def as_bool(v) -> bool:
    if isinstance(v, str):
        return v.strip().lower() in {"true", "1", "yes", "y"}
    return bool(v)


def find(data: dict, eid: int) -> dict:
    for e in data["entries"]:
        if e["id"] == eid:
            return e
    die(f"#{eid} not found")


def norm_label(s) -> str:
    # Store labels with minimal normalisation. Only the unambiguous Turkish
    # dotted capital I is fixed here ("İ".lower() would leave a combining dot);
    # lossy accent folding happens at comparison time in fold().
    return str(s).strip().replace("İ", "i").lower()


def fold(s: str) -> str:
    """Accent- and case-insensitive form used only for matching."""
    s = (s or "").replace("ı", "i").replace("İ", "i")
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).casefold()


def entry_text(e: dict) -> str:
    parts = [e.get("domain", ""), " ".join(e.get("tags", [])), e.get("context", ""),
             e.get("advice", ""), e.get("experiment", "")]
    parts += [a.get("text", "") + " " + (a.get("note") or "") for a in e.get("assumptions", [])]
    exp = e.get("expected", {})
    parts += [exp.get("change", ""), exp.get("signal", "")]
    r = e.get("result") or {}
    parts += [r.get("actual", ""), r.get("gap", ""), r.get("lesson", ""), r.get("new_assumption", "")]
    return fold(" ".join(p for p in parts if p))


# ---------- commands ----------

def cmd_add(args):
    inp = read_json_arg(args.file)
    for k in ("domain", "advice", "assumptions", "expected", "check_on"):
        if not inp.get(k):
            die(f"'{k}' is required")
    if not isinstance(inp["assumptions"], list):
        die("'assumptions' must be a list")
    exp = inp["expected"]
    if not isinstance(exp, dict) or not exp.get("signal"):
        die("'expected.signal' is required: which observation will tell us it worked?")
    assumptions = []
    for i, a in enumerate(inp["assumptions"], 1):
        if isinstance(a, str):
            a = {"text": a}
        if not isinstance(a, dict) or not a.get("text"):
            die(f"assumption {i} has no 'text'")
        assumptions.append({"id": f"A{i}", "text": a["text"],
                            "critical": as_bool(a.get("critical", False)),
                            "verdict": None, "note": None})
    if not any(a["critical"] for a in assumptions):
        die("mark at least one assumption \"critical\": true; the experiment tests it")
    tags = inp.get("tags", [])
    if isinstance(tags, str):
        tags = tags.split(",")
    if not isinstance(tags, list):
        die("'tags' must be a list")
    check_on = parse_date(inp["check_on"], "check_on")
    with lock():
        data = load()
        revises = inp.get("revises")
        if revises is not None:
            try:
                revises = int(revises)
            except (TypeError, ValueError):
                die("'revises' must be an entry id")
            find(data, revises)
        eid = max((e["id"] for e in data["entries"]), default=0) + 1
        entry = {
            "id": eid,
            "created": today(),
            "domain": norm_label(inp["domain"]),
            "tags": [norm_label(t) for t in tags if str(t).strip()],
            "context": inp.get("context", ""),
            "advice": inp["advice"],
            "assumptions": assumptions,
            "expected": {"change": exp.get("change", ""), "signal": exp["signal"]},
            "experiment": inp.get("experiment", ""),
            "check_on": check_on,
            "revises": revises,
            "status": "open",
            "result": None,
        }
        data["entries"].append(entry)
        save(data)
    print(f"#{eid} recorded, check-in {check_on}")


def cmd_result(args):
    inp = read_json_arg(args.file)
    status = inp.get("status")
    if status not in STATUSES:
        die(f"'status' must be one of {list(STATUSES)}")
    if not inp.get("actual"):
        die("'actual' is required: what really happened?")
    if status in NEEDS_LESSON and not inp.get("lesson"):
        die(f"'lesson' is required when status is {status}")
    verdicts = inp.get("verdicts", {})
    if not isinstance(verdicts, dict):
        die("'verdicts' must be an object: {\"A1\": \"broke\", ...}")
    with lock():
        data = load()
        e = find(data, args.id)
        if e["status"] != "open" and not args.force:
            die(f"#{args.id} is already closed ({e['status']}; lesson: "
                f"{(e['result'] or {}).get('lesson') or '-'}). Use --force to overwrite, or open "
                "a new entry with \"revises\" if this is a new attempt.")
        ids = {a["id"] for a in e["assumptions"]}
        for k, v in verdicts.items():
            val = v.get("verdict") if isinstance(v, dict) else v
            if k not in ids:
                die(f"assumption {k} is not in #{args.id} ({sorted(ids)})")
            if val not in VERDICTS:
                die(f"{k}: verdict must be one of {list(VERDICTS)}")
        for a in e["assumptions"]:
            v = verdicts.get(a["id"])
            if v is None:
                continue
            if isinstance(v, dict):
                a["verdict"], a["note"] = v.get("verdict"), v.get("note")
            else:
                a["verdict"] = v
        if status in NEEDS_LESSON and not any(a["verdict"] == "broke" for a in e["assumptions"]) \
                and not inp.get("new_assumption"):
            print("warning: the attempt did not work, but no assumption is marked 'broke' and there "
                  "is no 'new_assumption'. A hidden assumption was probably missed.", file=sys.stderr)
        missing = [a["id"] for a in e["assumptions"] if a["verdict"] is None]
        if missing:
            print(f"warning: no verdict for {', '.join(missing)}; use 'untested' if the "
                  "experiment did not test it.", file=sys.stderr)
        e["status"] = status
        e["result"] = {
            "date": today(),
            "actual": inp["actual"],
            "gap": inp.get("gap", ""),
            "lesson": inp.get("lesson", ""),
            "new_assumption": inp.get("new_assumption", ""),
            "source": inp.get("source", "user report"),
        }
        save(data)
    print(f"#{args.id} closed: {status}")


def cmd_postpone(args):
    with lock():
        data = load()
        e = find(data, args.id)
        if e["status"] != "open":
            die(f"#{args.id} is already closed ({e['status']})")
        new = parse_date(args.to, "--to")
        if new < today():
            die(f"cannot postpone into the past ({new})")
        e["check_on"] = new
        save(data)
    print(f"#{args.id} check-in moved to {new}")


def cmd_delete(args):
    with lock():
        data = load()
        e = find(data, args.id)
        children = [x["id"] for x in data["entries"] if x.get("revises") == args.id]
        if children and not args.force:
            die(f"#{args.id} is revised by {children}. Use --force to break the chain.")
        for x in data["entries"]:
            if x.get("revises") == args.id:
                x["revises"] = None
        data["entries"].remove(e)
        save(data)
    print(f"#{args.id} deleted")


def short(e: dict) -> str:
    crit = [a["text"] for a in e["assumptions"] if a["critical"]]
    line = f"#{e['id']} [{e['domain']}] {e['advice']}"
    line += f"\n    check-in: {e['check_on']} | signal: {e['expected']['signal']}"
    if crit:
        line += f"\n    critical assumption: {crit[0]}"
    return line


def cmd_due(args):
    if args.hook:
        f = ledger_dir(create=False) / "ledger.json"
        # Session-start reminder. Never fail, never print when there is nothing to say.
        if os.environ.get("ADVICE_DEBUGGER_NO_HOOK"):
            return
        try:
            if not f.exists():
                return
            with open(f, encoding="utf-8") as fh:
                data = json.load(fh)
            t = today()
            rows = sorted((e for e in data.get("entries", [])
                           if e.get("status") == "open" and e.get("check_on", "9999") <= t),
                          key=lambda x: x["check_on"])
            if rows:
                oldest = rows[0]
                more = f" ({len(rows) - 1} more due)" if len(rows) > 1 else ""
                print(f"advice-debugger: advice #{oldest['id']} \"{oldest['advice']}\" reached its "
                      f"check-in date{more}. When the conversation allows, ask the user in one line "
                      "how it went, then record it with the advice-debugger skill. Do not block "
                      "their request on it.")
        except Exception:
            pass
        return
    data = load()
    t = today()
    rows = [e for e in data["entries"] if e["status"] == "open" and (args.all or e["check_on"] <= t)]
    if args.count:
        print(len(rows))
        return
    if not rows:
        print("No open entries." if args.all else "Nothing is due.")
        return
    for e in sorted(rows, key=lambda x: x["check_on"]):
        print(short(e))


def full(e: dict) -> str:
    out = [f"#{e['id']} [{e['domain']}] {e['status']} (opened {e['created']})"]
    if e.get("tags"):
        out.append(f"  tags: {', '.join(e['tags'])}")
    if e.get("revises"):
        out.append(f"  revises: #{e['revises']}")
    if e.get("context"):
        out.append(f"  context: {e['context']}")
    out.append(f"  advice: {e['advice']}")
    for a in e["assumptions"]:
        flag = " (CRITICAL)" if a["critical"] else ""
        v = f" -> {a['verdict']}" if a["verdict"] else ""
        note = f" ({a['note']})" if a.get("note") else ""
        out.append(f"  {a['id']}{flag}: {a['text']}{v}{note}")
    out.append(f"  expected: {e['expected'].get('change') or '-'}")
    out.append(f"  signal: {e['expected']['signal']} | check-in: {e['check_on']}")
    if e.get("experiment"):
        out.append(f"  experiment: {e['experiment']}")
    r = e.get("result")
    if r:
        out.append(f"  OUTCOME ({r['date']}, source: {r['source']}): {r['actual']}")
        if r.get("gap"):
            out.append(f"  gap: {r['gap']}")
        if r.get("lesson"):
            out.append(f"  lesson: {r['lesson']}")
        if r.get("new_assumption"):
            out.append(f"  missed assumption: {r['new_assumption']}")
    return "\n".join(out)


def cmd_show(args):
    data = load()
    e = find(data, args.id)
    print(full(e))
    children = [x["id"] for x in data["entries"] if x.get("revises") == args.id]
    if children:
        print("  revised by: " + ", ".join(f"#{c}" for c in children))


def cmd_search(args):
    if not args.terms and not args.domain:
        die("give at least one term or --domain (for everything: due --all / lessons)")
    data = load()
    terms = [fold(t) for t in args.terms]
    dom = fold(args.domain) if args.domain else None
    hits = []
    for e in data["entries"]:
        if dom and dom not in fold(e["domain"]):
            continue
        txt = entry_text(e)
        score = sum(t in txt for t in terms)
        if score or not terms:
            hits.append((score, e))
    if not hits:
        print("No matches.")
        return
    hits.sort(key=lambda h: (-h[0], -h[1]["id"]))  # best match first, newest first
    for score, e in hits[:10]:
        if terms:
            print(f"({score}/{len(terms)} terms)")
        print(full(e))
        print()
    if len(hits) > 10:
        print(f"... {len(hits) - 10} more; narrow the terms.")


def cmd_lessons(args):
    data = load()
    dom = fold(args.domain) if args.domain else None
    rows = [e for e in data["entries"] if e["status"] != "open"
            and (not dom or dom in fold(e["domain"]))]
    if not rows:
        print("No closed entries yet.")
        return
    for e in sorted(rows, key=lambda x: (x["result"]["date"], x["id"]), reverse=True):
        r = e["result"]
        print(f"#{e['id']} [{e['domain']}] {e['status']}: {e['advice']}")
        for a in e["assumptions"]:
            if a["verdict"] == "broke":
                print(f"   x broke: {a['text']}" + (f" ({a['note']})" if a.get("note") else ""))
            elif a["verdict"] == "held" and a["critical"]:
                print(f"   + held (critical): {a['text']}")
        if r.get("new_assumption"):
            print(f"   ? missed assumption: {r['new_assumption']}")
        if r.get("lesson"):
            print(f"   -> lesson: {r['lesson']}")


def cmd_stats(args):
    data = load()
    by = {}
    for e in data["entries"]:
        by.setdefault(e["domain"], {}).setdefault(e["status"], 0)
        by[e["domain"]][e["status"]] += 1
    if not by:
        print("Ledger is empty.")
        return
    for d, c in sorted(by.items()):
        print(f"{d}: " + ", ".join(f"{k} {v}" for k, v in sorted(c.items())))


def render_md(data: dict) -> str:
    lines = ["# Advice Ledger", "",
             "_Generated by ledger.py. Do not edit; ledger.json is the source of truth._", ""]
    opens = sorted((e for e in data["entries"] if e["status"] == "open"), key=lambda x: x["check_on"])
    closed = sorted((e for e in data["entries"] if e["status"] != "open"), key=lambda x: -x["id"])
    lines += ["## Open experiments", ""]
    lines += [f"```\n{full(e)}\n```\n" for e in opens] or ["_none_", ""]
    lines += ["## Closed", ""]
    lines += [f"```\n{full(e)}\n```\n" for e in closed] or ["_none_", ""]
    return "\n".join(lines)


def cmd_render(args):
    data = load()
    out = ledger_dir() / "ledger.md"
    out.write_text(render_md(data), encoding="utf-8")
    print(out)


def main(argv=None):
    p = argparse.ArgumentParser(prog="ledger.py", description="advice-debugger ledger")
    sp = p.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("add"); a.add_argument("--file", required=True); a.set_defaults(fn=cmd_add)
    r = sp.add_parser("result"); r.add_argument("id", type=int); r.add_argument("--file", required=True)
    r.add_argument("--force", action="store_true"); r.set_defaults(fn=cmd_result)
    po = sp.add_parser("postpone"); po.add_argument("id", type=int); po.add_argument("--to", required=True)
    po.set_defaults(fn=cmd_postpone)
    de = sp.add_parser("delete"); de.add_argument("id", type=int); de.add_argument("--force", action="store_true")
    de.set_defaults(fn=cmd_delete)
    d = sp.add_parser("due"); d.add_argument("--all", action="store_true"); d.add_argument("--count", action="store_true")
    d.add_argument("--hook", action="store_true"); d.set_defaults(fn=cmd_due)
    s = sp.add_parser("search"); s.add_argument("terms", nargs="*"); s.add_argument("--domain"); s.set_defaults(fn=cmd_search)
    l = sp.add_parser("lessons"); l.add_argument("--domain"); l.set_defaults(fn=cmd_lessons)
    sh = sp.add_parser("show"); sh.add_argument("id", type=int); sh.set_defaults(fn=cmd_show)
    sp.add_parser("stats").set_defaults(fn=cmd_stats)
    sp.add_parser("render").set_defaults(fn=cmd_render)
    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
