# Repository Guidelines

## Project Structure & Module Organization
This repository is currently in idea stage and contains one source document: `idea.txt` (raw product discussion for the Manufacturing Personal Assistant concept). Keep it as the canonical context file until implementation starts.

When adding code, use a simple, explicit layout:
- `src/` for application code
- `tests/` for automated tests
- `docs/` for design notes, architecture, and product assumptions
- `data/` for sample or synthetic manufacturing inputs (never real customer data)

## Build, Test, and Development Commands
No build/test pipeline is configured yet. Use these baseline commands while the repo is documentation-first:
- `Get-Content idea.txt` to read the current concept notes
- `rg --files` to list tracked files quickly
- `rg "<term>"` to search decisions or requirements across docs

As soon as runtime code is added, define project scripts (for example in `Makefile` or package scripts) and update this section in the same PR.

## Coding Style & Naming Conventions
Use clear, minimal files and consistent names:
- Markdown/docs: kebab-case filenames (example: `line-balance-agent.md`)
- Python (if used): snake_case modules and 4-space indentation
- TypeScript (if used): camelCase variables, PascalCase types/components

Prefer small modules with one responsibility and add formatter/linter config with the first code PR.

## Testing Guidelines
There is no test framework yet. For any new executable code:
- Add a `tests/` directory that mirrors `src/`
- Name tests by behavior (`test_delay_detection.py`, `lineStatus.spec.ts`)
- Include at least one happy-path and one failure-path test per feature

Document exact run commands in the PR until CI is in place.

## Commit & Pull Request Guidelines
No Git history is available in this workspace yet, so adopt Conventional Commits from the start:
- `feat: add initial sensor event parser`
- `docs: refine manufacturing pitch assumptions`

PRs should include: purpose, key changes, verification steps/commands, and linked issue (if present). Add screenshots only for UI changes.

## Security & Configuration Tips
Do not commit credentials, plant identifiers, or raw customer production data. Keep secrets in local env files (for example `.env`) and commit only safe templates such as `.env.example`.
