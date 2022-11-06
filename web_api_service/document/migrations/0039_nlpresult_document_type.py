
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0038_auto_20201204_0005'),
    ]

    operations = [
        migrations.AddField(
            model_name='nlpresult',
            name='document_type',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='Document type'),
        ),
    ]
