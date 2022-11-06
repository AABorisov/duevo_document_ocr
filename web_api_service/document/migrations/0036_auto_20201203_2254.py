
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0035_auto_20201203_0205'),
    ]

    operations = [
        migrations.AddField(
            model_name='attributelink',
            name='description',
            field=models.TextField(blank=True, max_length=4000, null=True, verbose_name='Description'),
        ),
        migrations.CreateModel(
            name='NlpResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_number', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='Document number')),
                ('document_date', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='Document date')),
                ('issuing_authority', models.TextField(blank=True, max_length=4000, null=True, verbose_name='Issuing authority')),
                ('cadastral_number', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='Сadastral number')),
                ('administrative_district', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='Administrative district')),
                ('district', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='District')),
                ('address', models.TextField(blank=True, max_length=4000, null=True, verbose_name='Issuing authority')),
                ('object_name', models.TextField(blank=True, max_length=4000, null=True, verbose_name='Object name')),
                ('customer', models.TextField(blank=True, max_length=4000, null=True, verbose_name='Customer')),
                ('builder', models.TextField(blank=True, max_length=4000, null=True, verbose_name='Builder')),
                ('project_organization', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='Project organization')),
                ('project_author_manager', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='Project author manager')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
                ('nlp', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.nlp')),
            ],
        ),
    ]
