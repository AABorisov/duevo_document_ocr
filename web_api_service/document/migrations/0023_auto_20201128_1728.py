
from django.db import migrations, models
import django.db.models.deletion
import document.models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0022_remove_ocrtesseract_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='page_image',
            field=models.ImageField(null=True, upload_to=document.models.get_upload_path_pages),
        ),
        migrations.CreateModel(
            name='TesseractClassifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.document')),
                ('document_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='document.documenttype')),
            ],
            options={
                'db_table': 'document_tesseract_classifier',
            },
        ),
    ]
