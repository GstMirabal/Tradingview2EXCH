from django.db import models


class BinanceParams(models.Model):
    """A Django model to store parameters related to Binance alerts."""

    # Field to store the exchange associated with the alert.
    exchange = models.CharField(max_length=30)

    # Field to store the symbol associated with the alert.
    symbol = models.CharField(max_length=30)

    # Field to store the side associated with the alert (e.g., buy or sell).
    side = models.CharField(max_length=30)

    # Field to store the type of alert.
    type = models.CharField(max_length=30)

    # Field to store the size associated with the alert.
    size = models.DecimalField(max_digits=12, decimal_places=6)

    def save(self, *args: object, **kwargs: object) -> None:
        """Uppercase all string fields before saving.

        Args:
            *args: Positional arguments forwarded to the parent `save()`.
            **kwargs: Keyword arguments forwarded to the parent `save()`.
        """
        self.exchange = self.exchange.upper()
        self.symbol = self.symbol.upper()
        self.side = self.side.upper()
        self.type = self.type.upper()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return a human-readable representation of the instance.

        Returns:
            A dash-separated summary of the order parameters.
        """
        return f"{self.exchange} - {self.symbol} - {self.side} - {self.type} - {self.size}"
