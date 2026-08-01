"""Startup checks for configuration whose absence is silent.

Trading mode is the case this module exists for. A project that meant to place
real orders and never set the flag simply validates every order and executes
none, answering `201` throughout — nothing raises, and the only symptom is a
strategy that never seems to fill.
"""

from django.apps import AppConfig
from django.conf import settings
from django.core.checks import CheckMessage, register
from django.core.checks import Warning as DjangoWarning


@register()
def check_trading_mode_is_declared(
    app_configs: list[AppConfig] | None, **kwargs: object
) -> list[CheckMessage]:
    """Warn when nobody stated whether this deployment should trade.

    Fires only when `[binance].LIVE_TRADING` is absent. Writing `false` is a
    decision and draws no warning — a check that fires on a correct, explicit
    configuration is one people learn to ignore, and it would fail CI on every
    run of a pipeline that must never trade.

    Args:
        app_configs: Unused; the check is not per-app.
        **kwargs: Additional arguments passed by Django's check framework.

    Returns:
        list[CheckMessage]: A single `binance.W001` while live trading is
            disabled, an empty list once it is switched on.
    """
    if getattr(settings, 'BINANCE_LIVE_TRADING_DECLARED', False):
        return []
    return [
        DjangoWarning(
            '[binance].LIVE_TRADING is not declared, so orders are validated '
            'with new_order_test and never executed. No capital moves.',
            hint=(
                'Set LIVE_TRADING under [binance] in config.toml — `false` to '
                'silence this and keep dry runs, `true` to place real orders. '
                'Until Sprint #003 this was derived from DEBUG, so an upgraded '
                'deployment that relied on DEBUG=false to trade will stop '
                'trading until the flag is set to true. See '
                'docs/contracts/WEBHOOK_RECEIVER_CONTRACT.md, Execution mode.'
            ),
            id='binance.W001',
        )
    ]
