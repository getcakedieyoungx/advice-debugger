<h1 align="center">advice-debugger</h1>

<p align="center">
  <strong>Your AI gives you advice. It never finds out if it worked.<br/>Now it does.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/getcakedieyoungx/advice-debugger?style=flat" alt="License"></a>
  <a href="https://github.com/getcakedieyoungx/advice-debugger/actions/workflows/tests.yml"><img src="https://github.com/getcakedieyoungx/advice-debugger/actions/workflows/tests.yml/badge.svg" alt="Tests"></a>
  <img src="https://img.shields.io/badge/dependencies-0-brightgreen?style=flat" alt="Zero dependencies">
  <a href="https://www.patreon.com/monkeytax407"><img src="https://img.shields.io/badge/Patreon-support-F96854?style=flat&logo=patreon&logoColor=white" alt="Support on Patreon"></a>
</p>

<p align="center">
  <strong title="English">🇬🇧</strong> ·
  <a href=".github/readme/README.tr.md" title="Türkçe">🇹🇷</a> ·
  <a href=".github/readme/README.es.md" title="Español">🇪🇸</a> ·
  <a href=".github/readme/README.pt-BR.md" title="Português (Brasil)">🇧🇷</a> ·
  <a href=".github/readme/README.de.md" title="Deutsch">🇩🇪</a> ·
  <a href=".github/readme/README.zh-CN.md" title="简体中文">🇨🇳</a> ·
  <a href=".github/readme/README.ja.md" title="日本語">🇯🇵</a>
</p>

## Install

Paste this into Claude Code (or any coding agent):

```text
Install the advice-debugger skill from https://github.com/getcakedieyoungx/advice-debugger, following the repo's AGENTS.md.
```

Or as a Claude Code plugin:

```bash
claude plugin marketplace add getcakedieyoungx/advice-debugger
claude plugin install advice-debugger@advice-debugger
```

More options in [INSTALL.md](INSTALL.md).

## The problem

Code has tests. When a fix is wrong, something turns red.

Advice has nothing. Your assistant tells you to "post every day" or "cold-email 20 people", you try it, it fails for a reason nobody predicted, and next week the same assistant gives you the same advice in different words. It never saw the result.

## What changes

### A habit

<table>
<tr>
<td width="50%">

**Before**

> **You:** I tried posting every day like you said. Did 3 days, then quit. Writing was easy, but deciding what to write about every single day wore me out.
>
> **AI:** Consistency is key! Try setting a daily reminder, keep a list of ideas handy, and remember that small steps add up. Even a short post counts. You've got this! 💪

</td>
<td width="50%">

**After**

> **AI:** Logging #1's result. We assumed the bottleneck was *writing*. It turned out to be the *daily topic decision*. That assumption broke, so a reminder won't fix it.
>
> **Try for one week:** every Sunday, pick 5 topics and draft them in one 40-minute session. On weekdays, only publish the next draft.
>
> **Signal:** ≥5 posts in 7 days. Logged as #2 (revises #1), check-in Oct 8.

</td>
</tr>
</table>

### A codebase

<table>
<tr>
<td width="50%">

**Before**

> **You:** Two weeks ago you told me to split `shared/` into small packages. Now almost every PR touches four of them.
>
> **AI:** That's normal while a modular architecture settles in! Add Turborepo for caching, enforce boundaries with ESLint, and give it a few more weeks. It'll pay off. 🚀

</td>
<td width="50%">

**After**

> **AI:** Checked #5 against the last 14 PRs in `git log` instead of guessing:
>
> ```diff
>   expected   ≤ 2 packages touched per PR
> - actual     4 per PR, pricing + checkout changed together in 11/14
> ```
>
> **A1 broke:** "pricing and checkout change independently". Merge those two back into one package and keep the other splits.
>
> **Signal:** ≤ 2 packages per PR over the next 10 PRs. Logged as #6 (revises #5).

</td>
</tr>
</table>

What lands in the ledger for #5:

```json
{
  "status": "failed",
  "actual": "Median PR touched 4 packages; pricing and checkout changed together in 11 of 14 PRs.",
  "gap": "expected <= 2 packages per PR, got 4",
  "verdicts": {
    "A1": { "verdict": "broke", "note": "pricing and checkout are one unit of change" },
    "A2": "held"
  },
  "lesson": "Splitting modules that change together multiplied the packages touched per PR.",
  "source": "git log, last 14 PRs"
}
```

## How it works

Every piece of actionable advice becomes a small, falsifiable experiment in a local ledger:

1. **Assumptions:** what has to be true for this to work? One is marked *critical*.
2. **Expected outcome:** what should change, which observation proves it, and by when.
3. **Small experiment:** 3–14 days that test the critical assumption, not a month-long plan.
4. **Compare:** when you report back, each assumption is marked `held`, `broke` or `untested`. Missed assumptions get written down too.
5. **Next advice:** starts from the assumption that broke and links back to the old entry. Before answering, the assistant checks its draft against every broken assumption, which is meant to stop the same advice from coming back in new words.

The ledger is checked **before** new advice is given, so the lesson from last month's experiment shapes today's answer.

When a check-in date arrives, the plugin's session-start hook reminds the assistant to ask you, in one line, how it went. It stays silent when nothing is due.

## No character verdicts

One failed experiment never becomes "you lack discipline". Lessons are recorded as **condition + outcome** ("a routine that needed a fresh decision every day stalled on day 3"), because conditions can be redesigned and labels can't.

## Where it helps

| Area | What it learns |
|---|---|
| Learning | Which study method actually improves recall? |
| Business | Which outreach channel actually gets replies? |
| Software | Did that refactor really reduce maintenance? (git history answers it) |
| Planning | Where are your time estimates consistently off? |
| Content | Which production rhythm can you actually sustain? |

## The ledger

Plain JSON in `~/.advice-ledger/`, plus a readable `ledger.md`. A Python script (standard library only) does every write with a lock, validation and a backup. See an [example ledger](examples/example-ledger.md).

```text
$ python ledger.py lessons --domain content
#1 [content] abandoned: Post once every day
   x broke: The bottleneck is writing; picking topics is easy (the daily topic decision)
   -> lesson: A daily routine that needs a fresh decision every day stalled on day 3.
```

**Privacy:** the ledger is a local file and the script makes no network calls. The parts your assistant reads become part of that conversation, like any file it opens. Change the location with `ADVICE_LEDGER_DIR`, and turn off the reminder hook with `ADVICE_DEBUGGER_NO_HOOK=1`.

## Tune it

Fork it, edit [`skills/advice-debugger/SKILL.md`](skills/advice-debugger/SKILL.md), and install your fork. Run the tests with `python -m unittest discover -s tests`.

## Support

advice-debugger is free and MIT-licensed. If it saved you from one more round of recycled advice, you can support more tools like it on [Patreon](https://www.patreon.com/monkeytax407).

## License

[MIT](LICENSE).

Star ⭐ it if your assistant has ever handed you the same failed advice twice.
