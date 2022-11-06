
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0024_auto_20201129_1505'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='file',
            name='document_path',
        ),
        migrations.AddField(
            model_name='file',
            name='file_path',
            field=models.FileField(blank=True, null=True, upload_to='files/%Y/%m/%d/', verbose_name='File path'),
        ),
    ]
