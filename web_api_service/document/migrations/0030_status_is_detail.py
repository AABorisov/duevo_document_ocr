
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0029_file_is_processed'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='is_detail',
            field=models.BooleanField(default=True, verbose_name='Is detail'),
        ),
    ]
