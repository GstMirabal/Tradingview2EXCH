from rest_framework import serializers
from .models import webhook


class webhookSerializer(serializers.ModelSerializer):
    """
    Serializer for the webhook model.
    """
    # Specify ISO 8601 format for the 'time' field
    time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ")

    class Meta:
        model = webhook
        fields = '__all__'  # Include all fields from the model
        extra_kwargs = {
            'symbol': {'help_text': 'Field to store the symbol associated with the alert.'},
            'exchange': {'help_text': 'Field to store the exchange associated with the alert.'},
            'time': {'help_text': 'Field to store the time the alert was generated. Set as the primary key.'},
            'interval': {'help_text': 'Field to store the time interval associated with the alert.'},
            'size': {'help_text': 'Field to store the size associated with the alert.'},
            'side': {'help_text': 'Field to store the side associated with the alert (e.g., BUY or SELL).'},
            'price': {'help_text': 'Field to store the price in USDT of the alert.'},
            'orderId': {'help_text': 'Field to store the order ID associated with the alert.'},
            'marketPosition': {'help_text': 'Field to store the market position.'},
            'marketPrevPosition': {'help_text': 'Field to store the previous MARKET position.'},
            'type': {'help_text': 'Field to store the type of alert.'},
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
            raise serializers.ValidationError("Exchange is not allowed.")
        return value
