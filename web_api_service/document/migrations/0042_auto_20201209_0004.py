
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0041_auto_20201209_0004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classification',
            name='document',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.document'),
        ),
    ]
