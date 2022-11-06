
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0007_auto_20201027_2333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='page',
            name='document_link',
        ),
        migrations.AddField(
            model_name='page',
            name='page_link',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Page link'),
        ),
    ]
