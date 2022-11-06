
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0017_auto_20201114_2000'),
    ]

    operations = [
        migrations.AddField(
            model_name='nlp',
            name='ocr_word_ids',
            field=models.JSONField(default=None, null=True, verbose_name='OCR word IDs'),
        ),
        migrations.AddField(
            model_name='nlp',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Not recognized'), (1, 'Recognized'), (2, 'Operator recognized')], default=0, verbose_name='Status'),
        ),
    ]
