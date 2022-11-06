
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='document_link',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Document link'),
        ),
    ]
