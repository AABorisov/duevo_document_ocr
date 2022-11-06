
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0034_auto_20201203_0057'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nlp',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Not recognized'), (1, 'Recognized'), (2, 'Operator recognized'), (3, 'Operator add attribute with word ids'), (4, 'New attribute')], default=0, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='nlptesseract',
            name='ocr_word_ids',
            field=models.JSONField(blank=True, default=None, null=True, verbose_name='OCR word IDs'),
        ),
        migrations.AlterField(
            model_name='nlptesseract',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Not recognized'), (1, 'Recognized'), (2, 'Operator recognized'), (3, 'Operator add attribute with word ids'), (4, 'New attribute')], default=0, verbose_name='Status'),
        ),
    ]
