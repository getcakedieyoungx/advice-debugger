---
name: advice-debugger
description: Treats actionable advice as a hypothesis and tracks whether it worked, in a persistent local ledger. Extracts the assumptions behind the advice, records an expected outcome and measurable signal, designs a small experiment for the critical assumption, compares the real outcome, and derives the next advice from the assumption that broke instead of repeating itself. Use when the user asks for a plan, habit, study method, outreach, sales, content routine or work process they will apply over days or weeks; when they report how something they tried went ("tried it, didn't work", "did it 3 days then quit", "nobody replied"); when advising in an area with earlier advice; or when they mention the advice ledger. Not for one-off facts or work that finishes in this session.
license: MIT
metadata:
  tags: "advice, feedback-loop, experiments, habits, productivity, memory"
  category: "productivity"
---

# Advice Debugger

When code is wrong, a test goes red. Advice about life, work and learning has
no such signal: it sounds good, the user tries it, the outcome disappears, and
next conversation the same advice comes back in different words. This skill
builds the missing feedback loop: **every actionable piece of advice is a
hypothesis; its outcome is recorded; the next advice starts from the
assumption that broke.**

"Think harder" cannot do this. It needs a persistent record and real outcome
data, which `scripts/ledger.py` provides.

## The ledger

Run the script that sits next to this file:

```bash
python "<this skill's directory>/scripts/ledger.py" <command>
```

Use `python3` where `python` is not available. The ledger lives in
`~/.advice-ledger/` (override with `ADVICE_LEDGER_DIR`): `ledger.json` is the
source of truth, `ledger.md` is the human-readable view. Do not edit the JSON
by hand; the script locks, validates and keeps a backup.

| Command | When |
|---|---|
| `due` | advice topic comes up: has any check-in date arrived? |
| `lessons --domain d` | before advising: what broke here before? |
| `search term… [--domain d]` | find related past entries (best match first) |
| `stats` | which domains exist |
| `add --file f.json` | record new advice |
| `result ID --file f.json` | record the outcome (refuses closed entries) |
| `postpone ID --to YYYY-MM-DD` | the user has not tried it yet |
| `delete ID` | the user does not want it recorded |
| `show ID`, `render` | inspect |

Write the JSON to a temporary file first, then pass `--file`. Shell quoting
mangles non-ASCII text and backslashes, especially on Windows.

## The loop

### 0. Look back first

Before giving advice, run `due` and `lessons --domain <area>`. If you are not
sure which domain name was used, run `stats`, then `search` a few keywords.

- If a check-in is due, ask about the oldest one only, in one line: "Last
  time we tried batching posts once a week (#4). How did it go?" If more are
  due, say "two more experiments are open" and stop. Never hold the user's
  actual request hostage to the check-in.
- Compare your draft advice against every broken assumption in `lessons`.
  Does the draft rely on the same assumption? Then it is the same advice in
  new words, so change it. Search matches terms, not meaning; this
  comparison is your job.
- Say which history you used: "Last time the bottleneck turned out to be
  picking a topic every day, not writing, so…"

### 1. Extract assumptions

List what has to be true for the advice to work. Good assumptions are
testable and specific to this advice:

- Weak: "The user is motivated."
- Good: "They can spare 3 hours a week." / "People in this niche answer cold
  DMs." / "The bottleneck is writing, not choosing topics."

Mark at least one as **critical**: the one that sinks the whole plan if it is
false. It is usually the most uncertain one and the cheapest to test.

### 2. Define the expected outcome and signal

- **change**: what are we trying to change?
- **signal**: which concrete observation will tell us? A number or a yes/no:
  "≥5 posts in 7 days", "≥2 replies from 20 emails", "≥70% recall on day 3".
- **check_on**: when to look (the end of the experiment).

"Feeling better" is not a signal. If that is the goal, find a measurable
proxy ("days per week I opened the plan").

### 3. Design a small experiment

Instead of a month-long plan, propose the shortest, cheapest step (usually
3–14 days) that tests the critical assumption. A failed experiment should
still teach something: it should tell you which assumption broke.

### 4. Record it and say so

Record only when all three hold: the user will apply it themselves, applying
it takes at least a few days, and the outcome can be observed later.
Opinions ("which do you think is better?"), one-off facts and work that ends
in this session stay out. If several options were discussed, record only the
one the user decided to try.

Tell the user in one line; do not ask for permission at every step: "Logged
as #7, we'll check in on Oct 8. Say the word and I'll delete it." If they
decline, `delete ID`.

```json
{
  "domain": "content",
  "tags": ["x", "posting-routine"],
  "context": "wants a consistent posting habit on X",
  "advice": "Post once every day",
  "assumptions": [
    {"text": "The bottleneck is writing; picking topics is easy", "critical": true},
    {"text": "They can spare 20 minutes a day"}
  ],
  "expected": {"change": "consistent posting", "signal": ">=5 posts in 7 days"},
  "experiment": "one week, 20 minutes every evening",
  "check_on": "2026-10-08",
  "revises": null
}
```

`revises` is the id of the earlier entry this advice corrects, so the chain
stays visible.

### 5. Compare the outcome

When the user reports back (or permitted data arrives: analytics, git
history, test results, calendar), compare expectation and reality:

- **actual**: what happened, close to the user's own words.
- **gap**: the difference from the expectation.
- **verdicts**, one per assumption: `held`, `broke`, or `untested` (the
  experiment did not test it).
- **new_assumption**: something that decided the outcome but was never
  written down. This is often the most valuable finding.
- **lesson**: a condition-and-outcome sentence.
- **source**: "user report", "analytics export", "git log", ...
- **status**: `worked` / `partial` / `failed` / `abandoned` / `inconclusive`.

If information is missing, do not fill it in with guesses; ask one or two
sharp questions ("Which day did you stop, and what changed that day?").
`inconclusive` is an honest result when the data is thin.

```json
{
  "status": "abandoned",
  "actual": "Posted for 3 days, then stopped. Writing was easy; choosing a topic every day was exhausting.",
  "gap": "expected >=5, got 3",
  "verdicts": {
    "A1": {"verdict": "broke", "note": "the bottleneck was the daily topic decision"},
    "A2": "held"
  },
  "lesson": "A daily routine that needs a fresh decision every day stalled on day 3 from decision load.",
  "source": "user report"
}
```

### 6. Derive the next advice from what broke

The new advice should target the broken assumption directly and point to the
old entry with `revises`. Example: "Pick topics and draft three posts in one
weekly session" moves the decision load from daily to weekly. Test it with a
small experiment and record it too.

Assumptions that held are information as well: they show what carried the
success, so keep them in the next advice.

## No character verdicts

Never conclude or record a lasting trait from an experiment: "undisciplined",
"lazy", "can't focus". Lessons are always written as **condition and
outcome**: which setup, which step, what happened. Why it matters: a trait
label pushes the next advice toward "more willpower" and blocks redesign; a
condition record points at something that can change. Even a repeated
pattern is about conditions, not the person ("routines tied to evenings were
dropped in week one, three times").

## Edges

- If the user reports an outcome early, record it right away with `result`.
- If they have not tried it yet, `postpone`; that is not a failure.
- The ledger is personal and local. For health, money or relationships,
  write only as much detail as the advice needs.
- For medical, financial or legal matters the ledger does not replace a
  professional; experiments there stay within the user's own judgment and
  safe limits.
- Software advice usually has measurable signals: bug count, time spent per
  change, files touched, reopened issues. "Did this refactor reduce
  maintenance?" can often be answered from git history two weeks later.
