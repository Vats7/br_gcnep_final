# Generated by Django 3.2.9 on 2022-04-02 10:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import users.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20220401_1259'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employment',
            fields=[
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('employer', models.CharField(max_length=200, verbose_name='Name of Employer')),
                ('place', models.CharField(max_length=50, verbose_name='Place')),
                ('title', models.CharField(max_length=50, verbose_name='Title or Position')),
                ('description', models.TextField(max_length=200, verbose_name='Description')),
                ('start', models.DateField(verbose_name='From')),
                ('end', models.DateField(verbose_name='To')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employments', to='users.userprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('institute', models.CharField(max_length=200, verbose_name='Name and Place of Institute')),
                ('field_of_study', models.CharField(max_length=50, verbose_name='Field of Study')),
                ('degree', models.CharField(max_length=70, verbose_name='Diploma or Degree')),
                ('start', models.DateField(verbose_name='From')),
                ('end', models.DateField(verbose_name='To')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='educations', to='users.userprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(choices=[('SIGNATURE', 'Signature'), ('PASSPORT', 'Passport'), ('VISA', 'Visa'), ('APPROVAL', 'Approval'), ('AV', 'AudioVideo')], max_length=15)),
                ('file', models.FileField(help_text='Multiple Upload Allowed', upload_to=users.models.user_directory_path, validators=[users.models.validate_file_size], verbose_name='Upload File')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='users.userprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]