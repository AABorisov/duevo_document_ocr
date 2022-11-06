
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0013_auto_20201031_2126'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocSchemas',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc_id', models.IntegerField(blank=True, null=True)),
                ('page_id', models.IntegerField(blank=True, null=True)),
                ('link', models.TextField(blank=True, null=True)),
                ('orientation', models.IntegerField()),
                ('upper_left_y', models.IntegerField()),
                ('upper_left_x', models.IntegerField()),
                ('upper_right_y', models.IntegerField()),
                ('upper_right_x', models.IntegerField()),
                ('lower_right_y', models.IntegerField()),
                ('lower_right_x', models.IntegerField()),
                ('lower_left_y', models.IntegerField()),
                ('lower_left_x', models.IntegerField()),
            ],
            options={
                'db_table': 'doc_schemas',
                'managed': False,
            },
        ),
    ]
