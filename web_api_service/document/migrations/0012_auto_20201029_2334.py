
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0011_auto_20201029_1740'),
    ]

    operations = [
        migrations.RenameField(
            model_name='page',
            old_name='task_id',
            new_name='page_id',
        ),
    ]
