# Generated by Django 5.0.7 on 2024-07-25 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='webhook',
            fields=[
                ('symbol', models.CharField(max_length=30)),
                ('exchange', models.CharField(max_length=30)),
                ('time', models.DateTimeField(primary_key=True, serialize=False)),
                ('interval', models.DecimalField(decimal_places=2, max_digits=5)),
                ('size', models.DecimalField(decimal_places=6, max_digits=12)),
                ('side', models.CharField(max_length=30)),
                ('price', models.DecimalField(decimal_places=6, max_digits=12)),
                ('orderId', models.CharField(max_length=30)),
                ('marketPosition', models.DecimalField(decimal_places=6, max_digits=12)),
                ('marketPrevPosition', models.DecimalField(decimal_places=6, max_digits=12)),
                ('type', models.CharField(max_length=30)),
            ],
        ),
    ]
