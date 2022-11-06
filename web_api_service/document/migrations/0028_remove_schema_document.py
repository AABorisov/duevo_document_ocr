
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0027_ocr_document'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='schema',
            name='document',
        ),
    ]
