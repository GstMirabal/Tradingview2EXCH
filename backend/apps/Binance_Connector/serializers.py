from rest_framework import serializers

from .models import BinanceParams


class BinanceParamsSerializer(serializers.ModelSerializer):
    """Serializer for the BinanceParams model."""

    class Meta:
        model = BinanceParams
        fields = '__all__'  # Include all fields from the model
        extra_kwargs = {
            'exchange': {'help_text': 'Field to store the exchange associated with the alert.'},
            'symbol': {'help_text': 'Field to store the symbol associated with the alert.'},
            'side': {'help_text': 'Field to store the side associated with the alert (e.g., BUY or SELL).'},
            'type': {'help_text': 'Field to store the type of alert.'},
            'size': {'help_text': 'Field to store the size associated with the alert.'},
        }

    def validate_exchange(self, value: str) -> str:
        """Validate the 'exchange' field to ensure only 'BINANCE' is accepted.

        Args:
            value: The submitted value of the exchange field, in any case.

        Returns:
            The validated, uppercased value of the exchange field.

        Raises:
            serializers.ValidationError: If the exchange is not 'BINANCE'.
        """
        if value.upper() != 'BINANCE':
            raise serializers.ValidationError('Exchange is not allowed')
        return value.upper()
