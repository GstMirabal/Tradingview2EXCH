from django.db import migrations


class Migration(migrations.Migration):
    """Two-step rename to PascalCase.

    Django's migration state engine has a known issue with a `RenameModel`
    whose old and new names are identical once lowercased (e.g.
    'binanceParams' -> 'BinanceParams', both 'binanceparams'): the state
    machinery inserts the renamed model under the new (identical) key and
    then immediately removes that same key, deleting the model from state
    entirely (`ProjectState.rename_model`). Routing through an
    intermediate, genuinely different name avoids the collision.
    """

    dependencies = [
        ('Binance_Connector', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(old_name='binanceParams', new_name='TempBinanceParamsCasingFix'),
        migrations.RenameModel(old_name='TempBinanceParamsCasingFix', new_name='BinanceParams'),
    ]
