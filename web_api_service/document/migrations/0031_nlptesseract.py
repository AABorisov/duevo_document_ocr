
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0030_status_is_detail'),
    ]

    operations = [
        migrations.CreateModel(
            name='NlpTesseract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField(default=None, null=True, verbose_name='Position')),
                ('ocr_word_ids', models.JSONField(default=None, null=True, verbose_name='OCR word IDs')),
                ('status', models.SmallIntegerField(choices=[(0, 'Not recognized'), (1, 'Recognized'), (2, 'Operator recognized')], default=0, verbose_name='Status')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('ocr_text', models.TextField(blank=True, max_length=2000, null=True, verbose_name='Ocr text')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
                ('attribute', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.attribute')),
                ('document', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.document')),
            ],
            options={
                'db_table': 'document_nlp_tesseract',
            },
        ),
    ]
