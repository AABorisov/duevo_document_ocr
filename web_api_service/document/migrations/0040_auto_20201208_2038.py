
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0039_nlpresult_document_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nlpresult',
            name='document_date',
            field=models.DateField(blank=True, db_index=True, null=True, verbose_name='Document date'),
        ),
    ]
