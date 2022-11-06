
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0021_ocrtesseract_document'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ocrtesseract',
            name='document',
        ),
    ]
