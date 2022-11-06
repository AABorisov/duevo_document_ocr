
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0015_nlpocr'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Attribute name')),
                ('is_required', models.BooleanField(default=False, verbose_name='Is required')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_type_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Document type')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
            ],
            options={
                'db_table': 'document_document_type',
            },
        ),
        migrations.CreateModel(
            name='Nlp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField(default=None, null=True, verbose_name='Position')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
                ('attribute', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='document.attribute')),
                ('document', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.document')),
            ],
        ),
        migrations.CreateModel(
            name='Schema',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.TextField(blank=True, null=True, verbose_name='Link')),
                ('orientation', models.IntegerField(blank=True, null=True, verbose_name='Orientation')),
                ('upper_left_y', models.IntegerField(blank=True, null=True)),
                ('upper_left_x', models.IntegerField(blank=True, null=True)),
                ('upper_right_y', models.IntegerField(blank=True, null=True)),
                ('upper_right_x', models.IntegerField(blank=True, null=True)),
                ('lower_right_y', models.IntegerField(blank=True, null=True)),
                ('lower_right_x', models.IntegerField(blank=True, null=True)),
                ('lower_left_y', models.IntegerField(blank=True, null=True)),
                ('lower_left_x', models.IntegerField(blank=True, null=True)),
                ('document', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.document')),
                ('page', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.page')),
            ],
        ),
        migrations.CreateModel(
            name='Ocr',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ocr_text', models.TextField(blank=True, null=True, verbose_name='OCR text')),
                ('user_text', models.TextField(blank=True, null=True, verbose_name='OCR text')),
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
                ('document', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.document')),
                ('page', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.page')),
            ],
        ),
        migrations.CreateModel(
            name='NlpOcrElement',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.IntegerField(default=None, null=True, verbose_name='Position')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
                ('nlp', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.nlp')),
                ('ocr', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='document.attribute')),
            ],
            options={
                'db_table': 'document_nlp_ocr',
            },
        ),
        migrations.CreateModel(
            name='Classification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.document')),
                ('document_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='document.documenttype')),
            ],
        ),
        migrations.AddField(
            model_name='attribute',
            name='document_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='document.documenttype'),
        ),
    ]
