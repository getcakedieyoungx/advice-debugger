# Agent guide

Map for agents installing or changing [advice-debugger](https://github.com/getcakedieyoungx/advice-debugger).

## Installing for a user

1. Read `INSTALL.md` and pick the path for the user's agent.
2. For Claude Code, prefer the plugin commands. If the `claude` CLI is not
   available to you, copy `skills/advice-debugger/` into `~/.claude/skills/`.
3. Check that Python 3.9+ is available (`python3 --version` or `python --version`).
4. Do not create, edit or delete anything in the user's ledger
   (`~/.advice-ledger/` or `$ADVICE_LEDGER_DIR`) during installation.
5. Tell the user what was installed and where, and that the ledger stays local.

Only run commands needed for the installation the user asked for.

## Repository map

| Area | Location | Purpose |
|---|---|---|
| Skill (source of truth) | `skills/advice-debugger/SKILL.md` | The loop the assistant follows |
| Ledger script | `skills/advice-debugger/scripts/ledger.py` | All reads and writes of the ledger; stdlib only |
| Claude Code plugin | `.claude-plugin/`, `hooks/hooks.json` | Manifest, marketplace entry, session-start reminder |
| Tests | `tests/test_ledger.py` | End-to-end tests of the script, incl. the SKILL.md JSON examples |
| Docs | `README.md`, `INSTALL.md`, `.github/readme/` | User-facing docs and translations |

## Changing things

- Change `SKILL.md` first for behaviour changes. If you change the JSON
  examples in it, the tests check that the script still accepts them.
- Keep `ledger.py` dependency-free and backwards compatible with existing
  `ledger.json` files.
- Bump the version in `.claude-plugin/plugin.json` on every release; installed plugins only update when it changes.
- Run before submitting:

```bash
python -m unittest discover -s tests -v
claude plugin validate .
```
