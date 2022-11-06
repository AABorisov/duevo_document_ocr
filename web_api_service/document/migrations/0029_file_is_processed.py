
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0028_remove_schema_document'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='is_processed',
            field=models.BooleanField(default=False, verbose_name='Is processed'),
        ),
    ]
