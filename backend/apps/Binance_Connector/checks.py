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
    """Warn when live trading is off, so the silence is deliberate.

    Args:
        app_configs: Unused; the check is not per-app.
        **kwargs: Additional arguments passed by Django's check framework.

    Returns:
        list[CheckMessage]: A single `binance.W001` while live trading is
            disabled, an empty list once it is switched on.
    """
    if getattr(settings, 'BINANCE_LIVE_TRADING', False):
        return []
    return [
        DjangoWarning(
            'BINANCE_LIVE_TRADING is off: orders are validated with '
            'new_order_test and never executed. No capital moves.',
            hint=(
                'This is the default, and it is correct for development. To '
                'trade for real, set LIVE_TRADING = true under [binance] in '
                'config.toml. Until Sprint #003 this was derived from DEBUG, '
                'so an upgraded deployment that relied on DEBUG=false to '
                'trade will stop trading until the flag is set. See '
                'docs/contracts/WEBHOOK_RECEIVER_CONTRACT.md, Execution mode.'
            ),
            id='binance.W001',
        )
    ]
