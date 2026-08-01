"""Regression tests for the Sprint #003 audit findings.

Each was run against the unfixed code and observed to fail. A test that only
passes on repaired code is consistent with the defect never having existed.
"""

from unittest.mock import patch

from binance.error import ClientError
from django.core.checks import run_checks
from django.test import TestCase, override_settings

from apps.Webhook_Receiver.models import Webhook

URL = '/webhook-receiver/webhook/'
PASSPHRASE_CONFIG = {'django_settings': {'WEBHOOK_PASSPHRASE': 'test-passphrase'}}

PAYLOAD = {
    'passphrase': 'test-passphrase',
    'symbol': 'BTCUSDT',
    'exchange': 'BINANCE',
    'time': '2026-08-01T10:00:00Z',
    'interval': '30',
    'size': '0.001',
    'side': 'BUY',
    'price': '58000.0',
    'order_id': 'ALERT-1',
    'market_position': '0.01',
    'market_prev_position': '0.0',
    'type': 'MARKET',
}


def _rejection() -> ClientError:
    """Build the error Binance raises when it refuses an order outright."""
    return ClientError(400, -1013, 'Filter failure: LOT_SIZE', None, None)


@patch('apps.core.permissions.config', PASSPHRASE_CONFIG)
class RetryAfterRejectionTests(TestCase):
    """T-001: a rejected order used to block its own retry forever."""

    def _post(self) -> object:
        return self.client.post(URL, PAYLOAD, content_type='application/json')

    def test_rejected_order_can_be_retried(self) -> None:
        """The exchange refused it, so it provably did not execute."""
        with patch('apps.Webhook_Receiver.views.binance_service') as svc:
            svc.execute_order.side_effect = _rejection()
            first = self._post()
        self.assertEqual(first.status_code, 400)
        self.assertEqual(
            Webhook.objects.get(order_id='ALERT-1').execution_status,
            Webhook.ExecutionStatus.REJECTED,
        )

        with patch('apps.Webhook_Receiver.views.binance_service') as svc:
            svc.execute_order.return_value = {'orderId': 1, 'status': 'FILLED'}
            second = self._post()
            self.assertTrue(
                svc.execute_order.called,
                'the retry never reached the exchange; the trade is lost',
            )
        self.assertEqual(second.status_code, 201)
        self.assertEqual(
            Webhook.objects.get(order_id='ALERT-1').execution_status,
            Webhook.ExecutionStatus.EXECUTED,
        )
        self.assertEqual(Webhook.objects.filter(order_id='ALERT-1').count(), 1)

    def test_executed_order_is_not_retried(self) -> None:
        """A redelivery of a filled alert must not place a second order."""
        with patch('apps.Webhook_Receiver.views.binance_service') as svc:
            svc.execute_order.return_value = {'orderId': 1, 'status': 'FILLED'}
            self._post()

        with patch('apps.Webhook_Receiver.views.binance_service') as svc:
            again = self._post()
            self.assertFalse(svc.execute_order.called)
        self.assertEqual(again.status_code, 409)

    def test_undetermined_outcome_stays_blocked(self) -> None:
        """A timeout does not prove non-execution, so retry stays refused.

        This is the half a naive fix gets wrong: reopening every failure turns
        lost trades into duplicated ones, which is worse.
        """
        with patch('apps.Webhook_Receiver.views.binance_service') as svc:
            svc.execute_order.side_effect = TimeoutError('connection lost')
            first = self._post()
        self.assertEqual(first.status_code, 500)
        self.assertEqual(
            Webhook.objects.get(order_id='ALERT-1').execution_status,
            Webhook.ExecutionStatus.UNKNOWN,
        )

        with patch('apps.Webhook_Receiver.views.binance_service') as svc:
            second = self._post()
            self.assertFalse(
                svc.execute_order.called,
                'an order of unknown outcome was resent; it could double-fill',
            )
        self.assertEqual(second.status_code, 409)


class TradingModeTests(TestCase):
    """T-002: DEBUG used to decide whether an order was real."""

    def _call(self) -> str:
        from unittest.mock import MagicMock

        from apps.Binance_Connector.services import BinanceService

        svc = BinanceService()
        svc.api_key, svc.api_secret = 'k', 's'
        fake = MagicMock()
        svc._client = fake
        svc.execute_order('BTCUSDT', 'BUY', 'MARKET', '0.5')
        return 'new_order' if fake.new_order.called else 'new_order_test'

    @override_settings(BINANCE_LIVE_TRADING=False, DEBUG=False)
    def test_debug_false_alone_does_not_trade(self) -> None:
        """The whole point: DEBUG=false must no longer mean "move money"."""
        self.assertEqual(self._call(), 'new_order_test')

    @override_settings(BINANCE_LIVE_TRADING=True, DEBUG=True)
    def test_live_flag_trades_regardless_of_debug(self) -> None:
        """And the flag is what decides, not the presentation setting."""
        self.assertEqual(self._call(), 'new_order')

    @override_settings(BINANCE_LIVE_TRADING_DECLARED=False)
    def test_undeclared_trading_mode_is_reported_at_startup(self) -> None:
        """Nobody decided, and silence is the failure mode."""
        self.assertIn('binance.W001', {m.id for m in run_checks()})

    @override_settings(BINANCE_LIVE_TRADING_DECLARED=True, BINANCE_LIVE_TRADING=False)
    def test_an_explicit_no_is_not_reported(self) -> None:
        """Writing `false` is a decision.

        Warning on it would fire on every correct dry-run deployment and on
        every CI run — a pipeline must never trade — which is how a check
        becomes noise people filter out.
        """
        self.assertNotIn('binance.W001', {m.id for m in run_checks()})

    @override_settings(BINANCE_LIVE_TRADING_DECLARED=True, BINANCE_LIVE_TRADING=True)
    def test_an_explicit_yes_is_not_reported(self) -> None:
        """Trading deliberately is not a problem to report."""
        self.assertNotIn('binance.W001', {m.id for m in run_checks()})
