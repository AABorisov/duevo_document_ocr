
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0003_document_mime_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, null=True, unique=True, verbose_name='Status name')),
                ('description', models.TextField(blank=True, max_length=1000, null=True, verbose_name='Description')),
                ('color', models.CharField(blank=True, max_length=10, null=True, verbose_name='Color')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
            ],
        ),
        migrations.AddField(
            model_name='document',
            name='status',
            field=models.SmallIntegerField(choices=[(0, 'Male'), (1, 'Female'), (2, 'Other')], default=0, verbose_name='Status'),
        ),
    ]
