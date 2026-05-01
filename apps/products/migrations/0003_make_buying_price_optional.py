from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_rename_selling_price_to_buying_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="buying_price",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
    ]
