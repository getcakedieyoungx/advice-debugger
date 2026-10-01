# How to install

Requires Python 3.9+ on your `PATH` (as `python3` or `python`). No other dependencies.

## Claude Code (plugin, recommended)

```bash
claude plugin marketplace add getcakedieyoungx/advice-debugger
claude plugin install advice-debugger@advice-debugger
```

Restart Claude Code. The plugin includes the skill plus a session-start hook
that reminds the assistant when an experiment reaches its check-in date. The
hook prints nothing when nothing is due.

**Verify:** `claude plugin list` shows `advice-debugger` as enabled.

**Update:** `claude plugin marketplace update advice-debugger && claude plugin update advice-debugger@advice-debugger`, then restart.

**Uninstall:** `claude plugin uninstall advice-debugger`. Your ledger in
`~/.advice-ledger/` is kept; delete that folder yourself if you want it gone.

## Claude Code (skill only, no hook)

Copy the skill folder into your personal skills directory:

```bash
git clone https://github.com/getcakedieyoungx/advice-debugger
cp -r advice-debugger/skills/advice-debugger ~/.claude/skills/
```

On Windows (PowerShell):

```powershell
git clone https://github.com/getcakedieyoungx/advice-debugger
Copy-Item -Recurse advice-debugger\skills\advice-debugger "$HOME\.claude\skills\"
```

Without the hook, the assistant checks the ledger when an advice topic comes up
rather than at session start.

## Other agents

The skill is a standard `SKILL.md` folder with a stand-alone Python script.
Agents that load `SKILL.md` skills can use it by copying
`skills/advice-debugger/` into their skills directory. Agents that do not can
include the contents of `SKILL.md` in their instructions file (for example
`AGENTS.md` or `GEMINI.md`) and point the script path at the cloned repo.
Only Claude Code has been tested so far; reports for other agents are welcome.

## Settings

| Variable | Effect |
|---|---|
| `ADVICE_LEDGER_DIR` | Ledger location (default `~/.advice-ledger/`) |
| `ADVICE_DEBUGGER_NO_HOOK=1` | Silences the session-start reminder (any non-empty value) |
