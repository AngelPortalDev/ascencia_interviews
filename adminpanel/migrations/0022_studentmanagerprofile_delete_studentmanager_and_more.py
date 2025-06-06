# Generated by Django 5.1.5 on 2025-02-24 14:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0021_alter_studentmanager_options'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentManagerProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('institute_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_manager_profile', to='adminpanel.institute')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_manager_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'StudentManagerProfile',
                'verbose_name_plural': 'StudentManagerProfile',
            },
        ),
        migrations.DeleteModel(
            name='StudentManager',
        ),
        migrations.AddIndex(
            model_name='studentmanagerprofile',
            index=models.Index(fields=['institute_id'], name='adminpanel__institu_d72f04_idx'),
        ),
    ]
