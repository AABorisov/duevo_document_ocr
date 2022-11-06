
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0032_auto_20201201_0730'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='dictionary',
            field=models.TextField(blank=True, max_length=30000, null=True, verbose_name='Page dictionary'),
        ),
    ]
