
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0031_nlptesseract'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttributeLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attribute_link_name', models.CharField(max_length=255, null=True, unique=True, verbose_name='Attribute link name')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
            ],
            options={
                'db_table': 'document_attribute_link',
            },
        ),
        migrations.AddField(
            model_name='attribute',
            name='attribute_link',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='document.attributelink'),
        ),
    ]
