
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0033_page_dictionary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nlp',
            name='ocr_word_ids',
            field=models.JSONField(blank=True, default=None, null=True, verbose_name='OCR word IDs'),
        ),
    ]
