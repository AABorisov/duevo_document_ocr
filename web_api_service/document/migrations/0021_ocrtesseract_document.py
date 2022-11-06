
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0020_ocrtesseract'),
    ]

    operations = [
        migrations.AddField(
            model_name='ocrtesseract',
            name='document',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.document'),
        ),
    ]
