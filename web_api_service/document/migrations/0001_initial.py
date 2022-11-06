
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, null=True, verbose_name='Category name')),
                ('color', models.CharField(blank=True, max_length=10, null=True, verbose_name='Color')),
                ('description', models.TextField(blank=True, max_length=2000, null=True, verbose_name='Description')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_id', models.IntegerField(blank=True, null=True, verbose_name='Task ID')),
                ('doc_id', models.IntegerField(blank=True, null=True, verbose_name='Doc ID')),
                ('document_link', models.TextField(max_length=1000, null=True, verbose_name='Document link')),
                ('original_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Original name')),
                ('description', models.TextField(blank=True, max_length=2000, null=True, verbose_name='Description')),
                ('document_path', models.FileField(blank=True, null=True, upload_to='documents')),
                ('is_sent_to_server', models.BooleanField(default=False, verbose_name='Is sent')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created date')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Updated date')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='document.category')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
