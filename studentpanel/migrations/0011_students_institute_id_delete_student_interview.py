# Generated by Django 5.1.5 on 2025-02-12 11:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0014_merge_0012_merge_20250201_1647_0013_delete_students'),
        ('studentpanel', '0010_merge_20250212_1547'),
    ]

    operations = [
        migrations.AddField(
            model_name='students',
            name='institute_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='adminpanel.institute'),
        ),
        migrations.DeleteModel(
            name='Student_Interview',
        ),
    ]
