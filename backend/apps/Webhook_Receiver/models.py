from django.db import models


class Webhook(models.Model):
    """A single TradingView alert received and (optionally) forwarded to an exchange."""

    class ExecutionStatus(models.TextChoices):
        """What is known about this alert's order at the exchange.

        The distinction that matters is REJECTED against UNKNOWN. A rejected
        order provably did not execute, so resending the same `order_id` is
        safe. An unknown one might have executed with the response lost in
        transit, and resending it could place a second real order — so it stays
        blocked and needs a human.
        """

        PENDING = 'PENDING', 'Received, exchange not yet called'
        EXECUTED = 'EXECUTED', 'Accepted by the exchange'
        REJECTED = 'REJECTED', 'Refused by the exchange; safe to retry'
        UNKNOWN = 'UNKNOWN', 'Call failed without proving non-execution'

    # Outcome of the exchange call for this alert. Governs whether a repeated
    # `order_id` is a duplicate to reject or a retry to allow.
    execution_status = models.CharField(
        max_length=10,
        choices=ExecutionStatus.choices,
        default=ExecutionStatus.PENDING,
        db_index=True,
    )

    # Trading pair symbol associated with the alert.
    symbol = models.CharField(max_length=30)

    # Exchange the alert should be routed to.
    exchange = models.CharField(max_length=30)

    # Time the alert was generated, as reported by TradingView.
    time = models.DateTimeField(db_index=True)

    # Chart interval the alert fired on.
    interval = models.DecimalField(max_digits=5, decimal_places=2)

    # Order size associated with the alert.
    size = models.DecimalField(max_digits=12, decimal_places=6)

    # Order side: BUY or SELL.
    side = models.CharField(max_length=30)

    # Price in quote currency at alert time.
    price = models.DecimalField(max_digits=12, decimal_places=6)

    # TradingView-supplied order identifier. Unique so a retried webhook
    # delivery cannot trigger a second real order for the same alert.
    order_id = models.CharField(max_length=30, unique=True)

    # Strategy market position after this alert.
    market_position = models.DecimalField(max_digits=12, decimal_places=6)

    # Strategy market position before this alert.
    market_prev_position = models.DecimalField(max_digits=12, decimal_places=6)

    # Order type (e.g. MARKET).
    type = models.CharField(max_length=30)

    def __str__(self) -> str:
        """Return a human-readable representation of the alert.

        Returns:
            A dash-separated summary of the alert fields.
        """
        return (
            f'{self.symbol} - {self.exchange} - {self.time} - {self.interval} - '
            f'{self.size} - {self.side} - {self.price} - {self.order_id} - '
            f'{self.market_position} - {self.market_prev_position} - {self.type}'
        )
