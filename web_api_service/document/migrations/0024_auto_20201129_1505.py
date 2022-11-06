
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('document', '0023_auto_20201128_1728'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='category',
        ),
        migrations.RemoveField(
            model_name='document',
            name='document_path',
        ),
        migrations.RemoveField(
            model_name='document',
            name='mime_type',
        ),
        migrations.RemoveField(
            model_name='document',
            name='original_name',
        ),
        migrations.RemoveField(
            model_name='document',
            name='user',
        ),
        migrations.AlterField(
            model_name='nlp',
            name='ocr_text',
            field=models.TextField(blank=True, max_length=2000, null=True, verbose_name='Ocr text'),
        ),
        migrations.AlterField(
            model_name='ocr',
            name='ocr_text',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='OCR text'),
        ),
        migrations.AlterField(
            model_name='ocr',
            name='user_text',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='OCR text'),
        ),
        migrations.AlterField(
            model_name='ocrtesseract',
            name='ocr_text',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='OCR text'),
        ),
        migrations.AlterField(
            model_name='ocrtesseract',
            name='user_text',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='OCR text'),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_name', models.CharField(max_length=255, null=True, unique=True, verbose_name='Original name')),
                ('description', models.TextField(blank=True, db_index=True, max_length=2000, null=True, verbose_name='Description')),
                ('document_path', models.FileField(blank=True, null=True, upload_to='files/%Y/%m/%d/')),
                ('mime_type', models.CharField(max_length=50, null=True, verbose_name='Mime type')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='document.category')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='document',
            name='file',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.file'),
        ),
    ]
