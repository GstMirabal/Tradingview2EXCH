# Security Policy

## Supported Versions

This project ships from a single `main` branch — only the latest commit on `main` receives security fixes. There are no maintained release branches.

## Reporting a Vulnerability

Report privately through [GitHub Security Advisories](https://github.com/GstMirabal/Tradingview2EXCH/security/advisories/new) — open the *Security* tab and choose *Report a vulnerability*. Email **gst.mirabal@gmail.com** works too. Either way, not a public issue: for a defect in an order path, the issue is the exploit. Include:
- A description of the vulnerability and its potential impact.
- Steps to reproduce it.

You should expect an initial response within a few days. Confirmed vulnerabilities will be fixed on `main` and credited in the fix's commit/PR unless you request otherwise.

## Deploying this safely

This software executes **real trades with real money** using your Binance API credentials. If you deploy it, the following are your responsibility:

- **Never commit `.env`.** It's git-ignored, but verify with `git status` before every commit. `config.toml` is also ignored and should only ever contain `$VAR` placeholders.
- **Restrict your Binance API key.** Enable only the permissions you actually need, and use Binance's IP allowlist to restrict the key to your server's address. Never enable withdrawals.
- **Use a strong, unique `WEBHOOK_PASSPHRASE`.** It is the *only* thing standing between the public internet and an order being placed. Treat it like a password, and rotate it if you suspect exposure.
- **Serve over HTTPS behind a reverse proxy.** With `DEBUG=False` the app sets `SECURE_SSL_REDIRECT` and expects a proxy that terminates TLS and forwards `X-Forwarded-Proto` (see the README's production note). A webhook passphrase sent over plain HTTP is readable in transit.
- **Generate your own `DJANGO_SECRET_KEY`.** Never reuse one from a tutorial, an example file, or another project.
- **Verify `DEBUG` is actually false in production.** A truthy `DEBUG` disables every security header and exposes full tracebacks. `curl -I https://your-host/admin/login/` should show `Content-Security-Policy` and `Strict-Transport-Security` headers.
- **Nothing trades until you say so.** `[binance].LIVE_TRADING` is `false` by default, and while it is off every order goes to the SDK's dry-run endpoint (`new_order_test`). `manage.py check` reports `binance.W001` if you never declared the key at all. Confirm your alert payloads work there before switching it on.
- **Lock down the files holding your keys.** `.env` and `config.toml` are created world-readable by default. `chmod 600 .env config.toml` — every account on the host can otherwise read your Binance API key.
- **Rotating a key needs a restart.** Credentials are read once when the process starts, so replacing a compromised key in `.env` changes nothing until you restart the service.
- **Reconcile stuck orders against the exchange.** If a call to Binance fails without a definite answer — a timeout above all — the alert is recorded as `UNKNOWN` and refused on retry, because it may have filled with the response lost. That is deliberate: resending could place a second real order. Check the exchange, then decide.

## Disclaimer

This project is provided as-is under the MIT License, **without warranty of any kind**. Automated trading carries risk of financial loss. Neither the author nor any contributor is liable for trading losses, missed or duplicated orders, exchange API failures, or any other damages arising from use of this software. You are solely responsible for the trades your deployment places.
