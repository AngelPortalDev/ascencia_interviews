# Generated by Django 5.1.5 on 2025-01-28 06:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0008_commonquestion'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='course_name',
            new_name='course_name',
        ),
    ]
