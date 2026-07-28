from django.db import migrations, models


class Migration(migrations.Migration):
    """Two-step model rename (see Binance_Connector 0002 for why) plus field renames."""

    dependencies = [
        ('Webhook_Receiver', '0002_webhook_id_alter_webhook_time'),
    ]

    operations = [
        migrations.RenameModel(old_name='webhook', new_name='TempWebhookCasingFix'),
        migrations.RenameModel(old_name='TempWebhookCasingFix', new_name='Webhook'),
        migrations.RenameField(
            model_name='Webhook', old_name='orderId', new_name='order_id'
        ),
        migrations.RenameField(
            model_name='Webhook', old_name='marketPosition', new_name='market_position'
        ),
        migrations.RenameField(
            model_name='Webhook',
            old_name='marketPrevPosition',
            new_name='market_prev_position',
        ),
        migrations.AlterField(
            model_name='Webhook',
            name='order_id',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]
