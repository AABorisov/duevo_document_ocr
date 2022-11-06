
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0010_page_page_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='is_sent_to_server',
        ),
        migrations.AddField(
            model_name='document',
            name='is_processed',
            field=models.BooleanField(default=False, verbose_name='Is processed'),
        ),
        migrations.AddField(
            model_name='page',
            name='is_sent_to_server',
            field=models.BooleanField(default=False, verbose_name='Is sent'),
        ),
    ]
