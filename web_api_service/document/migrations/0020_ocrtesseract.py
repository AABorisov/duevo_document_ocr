
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0019_nlp_ocr_text'),
    ]

    operations = [
        migrations.CreateModel(
            name='OcrTesseract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ocr_text', models.TextField(blank=True, db_index=True, null=True, verbose_name='OCR text')),
                ('user_text', models.TextField(blank=True, db_index=True, null=True, verbose_name='OCR text')),
                ('upper_left_y', models.IntegerField(blank=True, null=True)),
                ('upper_left_x', models.IntegerField(blank=True, null=True)),
                ('upper_right_y', models.IntegerField(blank=True, null=True)),
                ('upper_right_x', models.IntegerField(blank=True, null=True)),
                ('lower_right_y', models.IntegerField(blank=True, null=True)),
                ('lower_right_x', models.IntegerField(blank=True, null=True)),
                ('lower_left_y', models.IntegerField(blank=True, null=True)),
                ('lower_left_x', models.IntegerField(blank=True, null=True)),
                ('status', models.SmallIntegerField(blank=True, default=2, null=True, verbose_name='Status')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
                ('page', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.page')),
            ],
            options={
                'db_table': 'document_ocr_tesseract',
            },
        ),
    ]
