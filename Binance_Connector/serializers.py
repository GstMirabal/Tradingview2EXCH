from rest_framework import serializers
from .models import binanceParams


class binanceParamsserializers(serializers.ModelSerializer):
    """
    Serializer for the binanceParams model.
    """

    class Meta:
        model = binanceParams
        fields = '__all__'  # Include all fields from the model
        extra_kwargs = {
            'exchange': {'help_text': 'Field to store the exchange associated with the alert.'},
            'symbol': {'help_text': 'Field to store the symbol associated with the alert.'},
            'side': {'help_text': 'Field to store the side associated with the alert (e.g., BUY or SELL).'},
            'type': {'help_text': 'Field to store the type of alert.'},
            'size': {'help_text': 'Field to store the size associated with the alert.'},
        }

    def validate_exchange(self, value):
        """
        Validate the 'exchange' field to ensure only 'BINANCE' is accepted.

        Args:
            value (str): The value of the exchange field.

        Returns:
            str: The validated value of the exchange field.

        Raises:
            serializers.ValidationError: If the exchange is not 'BINANCE'.
        """
        if value != 'BINANCE':
            raise serializers.ValidationError("Exchange is not allowed")
        return value
