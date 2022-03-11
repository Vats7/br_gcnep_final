# Generated by Django 3.2.9 on 2022-02-07 10:15

from django.db import migrations, models
import django.utils.timezone
import lms.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user_unique_id', models.CharField(max_length=15, unique=True)),
                ('permission', models.CharField(choices=[('PRIMARY', 'Primary Trainer'), ('OTHER', 'Other Trainer'), ('TRAINEE', 'Trainee'), ('OBSERVER', 'Observer')], max_length=15)),
                ('training_status', models.BooleanField(default=False)),
                ('notes', models.CharField(blank=True, max_length=64, verbose_name='Optional Notes')),
                ('start_at', models.DateTimeField(blank=True, null=True)),
                ('end_at', models.DateTimeField(blank=True, null=True)),
                ('joined_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Enrolment',
                'verbose_name_plural': 'Enrolments',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Training',
            fields=[
                ('unique_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=50, verbose_name='Title')),
                ('description', models.TextField(max_length=200, verbose_name='Description')),
                ('training_type', models.CharField(choices=[('WORKSHOP', 'Workshop'), ('PROGRAM', 'Program'), ('MEETING', 'Meeting'), ('OTHER', 'Other')], help_text='Please Select the relevant training type from the dropdown', max_length=10, verbose_name='Training Type')),
                ('other', models.CharField(blank=True, help_text='Only required if Training Type is "OTHER"', max_length=30, verbose_name='Type')),
                ('main_image', models.ImageField(help_text='Upload an Image(Flyer). Should be less than 5MB', upload_to='trainings/main_image/', validators=[lms.models.validate_file_size], verbose_name='Image')),
                ('content', models.CharField(blank=True, max_length=100)),
                ('director', models.CharField(blank=True, max_length=30)),
                ('coordinator', models.CharField(blank=True, max_length=30)),
                ('start_at', models.DateTimeField(blank=True, null=True)),
                ('end_at', models.DateTimeField(blank=True, null=True)),
                ('assignment', models.ManyToManyField(blank=True, to='cms.Assignment')),
            ],
            options={
                'verbose_name': ' Training',
                'verbose_name_plural': ' Trainings',
                'ordering': ['-created_at'],
            },
        ),
    ]