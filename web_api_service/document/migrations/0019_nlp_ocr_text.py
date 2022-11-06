
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0018_auto_20201115_1048'),
    ]

    operations = [
        migrations.AddField(
            model_name='nlp',
            name='ocr_text',
            field=models.TextField(blank=True, max_length=2000, null=True, verbose_name='Status'),
        ),
    ]
