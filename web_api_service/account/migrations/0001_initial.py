
import account.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('password', models.CharField(default=None, max_length=128, null=True, verbose_name='Password')),
                ('email', models.EmailField(max_length=150, unique=True, verbose_name='Email')),
                ('first_name', models.CharField(max_length=30, null=True, verbose_name='first name')),
                ('last_name', models.CharField(max_length=150, null=True, verbose_name='last name')),
                ('gender', models.SmallIntegerField(choices=[(0, 'Male'), (1, 'Female'), (2, 'Other')], default=0, verbose_name='Gender')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', account.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(blank=True, null=True, upload_to='profile_images/%Y/%m/%d/')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='Birthday')),
                ('job_title', models.CharField(blank=True, db_index=True, max_length=150, null=True, verbose_name='Job title')),
                ('phone', models.CharField(blank=True, db_index=True, max_length=20, null=True, verbose_name='Phone')),
                ('company_name', models.CharField(blank=True, db_index=True, max_length=150, null=True, verbose_name='Company name')),
                ('linkedin', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='Linkedin')),
                ('facebook', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='Facebook')),
                ('vkontakte', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='Vkontakte')),
                ('instagram', models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='Instagram')),
                ('notes', models.TextField(blank=True, max_length=1000, null=True, verbose_name='Notes')),
                ('email_notify', models.SmallIntegerField(choices=[(0, 'Disable'), (1, 'Enable')], default=0, verbose_name='Email notify')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
