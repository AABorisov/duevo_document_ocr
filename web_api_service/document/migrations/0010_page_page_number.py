
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0009_page_original_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='page_number',
            field=models.IntegerField(blank=True, null=True, verbose_name='Page number'),
        ),
    ]
