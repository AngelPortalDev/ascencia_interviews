# Generated by Django 4.2.19 on 2025-07-07 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studentpanel', '0039_studentinterviewlink_assigned_question_ids'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentinterviewlink',
            name='transcript_text',
            field=models.TextField(blank=True, help_text='Transcript of the merged interview video', null=True),
        ),
    ]
