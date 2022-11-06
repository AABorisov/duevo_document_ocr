
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0037_auto_20201203_2333'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nlpresult',
            name='nlp',
        ),
        migrations.AddField(
            model_name='nlpresult',
            name='document',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.document'),
        ),
    ]
