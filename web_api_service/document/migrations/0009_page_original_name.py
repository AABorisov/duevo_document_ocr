
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0008_auto_20201027_2340'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='original_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Original name'),
        ),
    ]
