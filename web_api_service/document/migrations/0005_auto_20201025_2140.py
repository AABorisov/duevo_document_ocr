
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0004_auto_20201025_2127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='status',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='document.status'),
        ),
    ]
