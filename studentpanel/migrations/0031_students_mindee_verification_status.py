# Generated by Django 4.2.19 on 2025-03-17 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studentpanel', '0030_remove_studentinterviewlink_total_grammer_scores_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='students',
            name='mindee_verification_status',
            field=models.CharField(choices=[('unverified', 'Unverified'), ('verified', 'Verified'), ('rejected', 'Rejected')], default='Inporgress', max_length=20),
        ),
    ]
