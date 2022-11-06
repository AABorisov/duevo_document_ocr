
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0005_auto_20201025_2140'),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, max_length=2000, null=True, verbose_name='Description')),
                ('page', models.ImageField(null=True, upload_to='pages')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
                ('document', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='document.document')),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='document.status')),
            ],
        ),
    ]
