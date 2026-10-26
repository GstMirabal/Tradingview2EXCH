# Skill Assignment — Sprint 004 (dependency security and framework pin)

Source: `docs/sprints/004-backend-dependencies/IMPLEMENTATION_PLAN.md`.
Phase 4.2 of `workflows/pipeline_workflow.md`. Drafted from this template.

Mode: **Claude Code, single session**, `delegation_mode: sequential`.

---

## 1. Priority ladder (record every rung)

| Rung | Source | Result | Evidence |
| :--- | :--- | :--- | :--- |
| P1 | `skills/manifest_skills.json` | No skill needed | Every unit is a `gh pr merge`, a `git checkout` of a tag, or a one-line documentation edit |
| P2 | `autoskills-3rd` | not reached | — |
| P3 | `https://skills.sh/` | not reached | — |
| P4 | Three-File Standard at Destination | not reached | — |

---

## 2. Per-unit tool resolution

| Unit | Skill / tool | Destination | P1–P4 trail |
| :--- | :--- | :--- | :--- |
| 1-4 | `gh` CLI | N/A | P1 terminated |
| 5 | `git`, `.agents/scripts/install_claude.sh` | N/A | P1 terminated |
| 6 | none | N/A | P1 terminated |

---

## 3. Skills used

| Skill | Why |
| :--- | :--- |
| None | No unit required a skill |

## 4. Skills considered and rejected

| Candidate | Why rejected |
| :--- | :--- |
| `django-verification-3rd` | The Tester gate ran `pytest` and `manage.py check` directly; the skill would have wrapped the same two commands |
| `python-quality-auditor` | The QA gate needed only `ruff check` and `ruff format --check`, both run directly |

## 5. Gaps

None.
