# Security Policy

## Supported Versions

This project ships from a single `main` branch — only the latest commit on `main` receives security fixes. There are no maintained release branches.

## Reporting a Vulnerability

Please report suspected vulnerabilities privately by emailing **gst.mirabal@gmail.com** rather than opening a public issue. Include:
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
- **Start in test mode.** With `DEBUG=True` the Binance service calls the SDK's dry-run endpoint (`new_order_test`) instead of placing real orders. Confirm your alert payloads work there first.

## Disclaimer

This project is provided as-is under the MIT License, **without warranty of any kind**. Automated trading carries risk of financial loss. Neither the author nor any contributor is liable for trading losses, missed or duplicated orders, exchange API failures, or any other damages arising from use of this software. You are solely responsible for the trades your deployment places.
