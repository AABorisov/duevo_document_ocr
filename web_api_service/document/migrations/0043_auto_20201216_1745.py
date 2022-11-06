
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0042_auto_20201209_0004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribute',
            name='document_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.documenttype'),
        ),
        migrations.AlterField(
            model_name='nlp',
            name='attribute',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.attribute'),
        ),
    ]
