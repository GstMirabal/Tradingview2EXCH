# Contributing

Thanks for considering a contribution. This is a small Django project — the setup is quick and the rules are few.

## Getting set up

Follow the [Installation & Configuration](README.md#installation--configuration) steps in the README, then confirm everything works before you change anything:

```bash
cd backend
python manage.py test    # 63 tests, all should pass
```

## Before you open a PR

Three checks, all of which CI-less as this repo currently is, we ask you to run locally:

```bash
ruff check backend/                 # must report zero issues
ruff format backend/                # formats to this project's style
cd backend && python manage.py test # must stay green
```

New behavior needs a test. This project has been bitten repeatedly by bugs that unit tests missed because they mocked away the very thing that was broken — if you touch configuration loading, security settings, or anything in the request path, prefer a test that exercises the real code path over one that patches around it.

## Conventions

- **Python**: `snake_case` for functions/variables, `PascalCase` for classes, type hints on all arguments and return values, Google-style docstrings (`Args:`/`Returns:`). `ruff` enforces most of this.
- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/) (e.g. `fix(webhook): reject duplicate order_id`).
- **Branches**: work on a feature branch, open a PR into `main` — don't commit directly to `main`.

## Things to know before changing certain areas

- **`config.toml` / `.env`**: `config.toml` is git-ignored and holds only `$VAR` placeholders; real values live in `.env` (never committed). If you add a config key, document it in **both** `config.toml.example` and `.env.example`, and remember that `envtoml` substitutes an unset variable as an **empty string**, not a missing key — use `or 'default'`, not `dict.get(key, default)`.
- **Security settings** (`backend/config/settings.py` Section 3): these only activate when `DEBUG` is falsy. Test production behavior with a real `DEBUG="False"` value in your environment, not just `@override_settings(DEBUG=False)` — the two are not equivalent here.
- **The webhook contract**: field names in `Webhook`'s serializer are the exact JSON keys TradingView alerts send. Renaming one is a breaking change for every already-configured alert — see [`docs/decisions/ADR-0001`](docs/decisions/ADR-0001-governance-casing-rename.md) for how that was handled last time.
- **Migrations**: commit them alongside the model change. Run `python manage.py makemigrations --check --dry-run` to confirm nothing is missing.

## Reporting bugs and requesting features

Use the [issue templates](.github/ISSUE_TEMPLATE/). For anything security-sensitive, **don't open a public issue** — see [`SECURITY.md`](SECURITY.md).

## Governance

This project is governed by the [`.agents`](https://github.com/GstMirabal/.agents) pipeline, which is why you'll see `docs/architecture/*_BLUEPRINT.md`, `docs/decisions/`, and a `#[Sprint_ID]` suffix on historical commit messages. You don't need to adopt any of that to contribute — the checks above are what matter for a PR.

## Code of Conduct

By participating, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).
