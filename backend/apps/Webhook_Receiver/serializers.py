from rest_framework import serializers

from .models import Webhook


class WebhookSerializer(serializers.ModelSerializer):
    """Serializer for the Webhook model."""

    # Specify ISO 8601 format for the 'time' field
    time = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%SZ')

    class Meta:
        model = Webhook
        fields = '__all__'  # Include all fields from the model
        extra_kwargs = {
            'symbol': {
                'help_text': 'Field to store the symbol associated with the alert.'
            },
            'exchange': {
                'help_text': 'Field to store the exchange associated with the alert.'
            },
            'time': {'help_text': 'Field to store the time the alert was generated.'},
            'interval': {'help_text': 'Field to store the time interval of the alert.'},
            'size': {'help_text': 'Field to store the size associated with the alert.'},
            'side': {
                'help_text': 'Field to store the side (BUY or SELL) of the alert.'
            },
            'price': {'help_text': 'Field to store the price in USDT of the alert.'},
            'order_id': {
                'help_text': 'Field to store the order ID associated with the alert.'
            },
            'market_position': {'help_text': 'Field to store the market position.'},
            'market_prev_position': {
                'help_text': 'Field to store the previous market position.'
            },
            'type': {'help_text': 'Field to store the type of alert.'},
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
            raise serializers.ValidationError('Exchange is not allowed.')
        return value.upper()
