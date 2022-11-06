
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0036_auto_20201203_2254'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='nlpresult',
            table='document_nlp_result',
        ),
    ]
