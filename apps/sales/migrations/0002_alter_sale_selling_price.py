from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sale",
            name="selling_price",
            field=models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Unit Price"),
        ),
    ]
