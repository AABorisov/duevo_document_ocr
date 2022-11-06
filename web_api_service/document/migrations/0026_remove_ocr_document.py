
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0025_auto_20201129_1518'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ocr',
            name='document',
        ),
    ]
