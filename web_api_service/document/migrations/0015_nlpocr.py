
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0014_docschemas'),
    ]

    operations = [
        migrations.CreateModel(
            name='NlpOcr',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'nlp_ocr',
                'managed': False,
            },
        ),
    ]
