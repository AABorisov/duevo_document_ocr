
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0006_page'),
    ]

    operations = [
        migrations.RenameField(
            model_name='page',
            old_name='page',
            new_name='page_image',
        ),
        migrations.RemoveField(
            model_name='document',
            name='doc_id',
        ),
        migrations.RemoveField(
            model_name='document',
            name='document_link',
        ),
        migrations.RemoveField(
            model_name='document',
            name='task_id',
        ),
        migrations.AddField(
            model_name='page',
            name='doc_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Doc ID'),
        ),
        migrations.AddField(
            model_name='page',
            name='document_link',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Document link'),
        ),
        migrations.AddField(
            model_name='page',
            name='task_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Task ID'),
        ),
    ]
