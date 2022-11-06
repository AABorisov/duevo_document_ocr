
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0040_auto_20201208_2038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classification',
            name='document',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.document', unique=True),
        ),
    ]
