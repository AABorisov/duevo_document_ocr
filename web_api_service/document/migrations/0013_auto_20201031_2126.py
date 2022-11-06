
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0012_auto_20201029_2334'),
    ]

    operations = [
        migrations.CreateModel(
            name='BtiDocuments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_id', models.IntegerField(blank=True, null=True)),
                ('number', models.TextField(blank=True, null=True)),
                ('date', models.TextField(blank=True, null=True)),
                ('issuing_authority', models.TextField(blank=True, null=True)),
                ('documentation_source', models.TextField(blank=True, null=True)),
                ('date_of_completion', models.TextField(blank=True, null=True)),
                ('object_name', models.TextField(blank=True, null=True)),
                ('inventory_number', models.TextField(blank=True, null=True)),
                ('main_characteristic_value', models.TextField(blank=True, null=True)),
                ('year_built', models.TextField(blank=True, null=True)),
                ('commissioning_year', models.TextField(blank=True, null=True)),
                ('cadastral_number_zu', models.TextField(blank=True, null=True)),
                ('cadastral_number_oks', models.TextField(blank=True, null=True)),
                ('building_plan_stamp_recognition', models.TextField(blank=True, null=True)),
                ('building_plan_stamp_date_of_completion', models.TextField(blank=True, null=True)),
                ('building_plan_stamp_date_of_modification', models.TextField(blank=True, null=True)),
                ('building_plan_stamp_owner_name', models.TextField(blank=True, null=True)),
                ('object_composition_object', models.TextField(blank=True, null=True)),
                ('object_composition_name', models.TextField(blank=True, null=True)),
                ('object_composition_year', models.TextField(blank=True, null=True)),
                ('object_composition_area', models.TextField(blank=True, null=True)),
                ('land_explication_explication', models.TextField(blank=True, null=True)),
                ('land_explication_area', models.TextField(blank=True, null=True)),
                ('land_explication_address', models.TextField(blank=True, null=True)),
                ('land_explication_purpose', models.TextField(blank=True, null=True)),
                ('land_explication_marks', models.TextField(blank=True, null=True)),
                ('land_explication_date', models.TextField(blank=True, null=True)),
                ('land_explication_date_of_modification', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'bti_documents',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DocClasses',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('class_name', models.CharField(max_length=2048)),
            ],
            options={
                'db_table': 'doc_classes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DocClassificationResults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_id', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'doc_classification_results',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OcrResults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_id', models.IntegerField(blank=True, null=True)),
                ('ocr_text', models.TextField(blank=True, null=True)),
                ('upper_left_y', models.IntegerField(blank=True, null=True)),
                ('upper_left_x', models.IntegerField(blank=True, null=True)),
                ('upper_right_y', models.IntegerField(blank=True, null=True)),
                ('upper_right_x', models.IntegerField(blank=True, null=True)),
                ('lower_right_y', models.IntegerField(blank=True, null=True)),
                ('lower_right_x', models.IntegerField(blank=True, null=True)),
                ('lower_left_y', models.IntegerField(blank=True, null=True)),
                ('lower_left_x', models.IntegerField(blank=True, null=True)),
                ('status', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'ocr_results',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SvidAgrDocuments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_id', models.IntegerField(blank=True, null=True)),
                ('number', models.TextField(blank=True, null=True)),
                ('date', models.TextField(blank=True, null=True)),
                ('issuing_authority', models.TextField(blank=True, null=True)),
                ('administrative_district', models.TextField(blank=True, null=True)),
                ('district', models.TextField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('object_name', models.TextField(blank=True, null=True)),
                ('functional_purpose_of_object', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'svid_agr_documents',
                'managed': False,
            },
        ),
        migrations.AlterField(
            model_name='page',
            name='page_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Page ID'),
        ),
    ]
