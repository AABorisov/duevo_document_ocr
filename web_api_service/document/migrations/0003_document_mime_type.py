
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0002_auto_20201025_1227'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='mime_type',
            field=models.CharField(max_length=50, null=True, verbose_name='Mime type'),
        ),
    ]
