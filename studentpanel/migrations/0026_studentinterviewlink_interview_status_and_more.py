# Generated by Django 4.2.19 on 2025-03-03 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studentpanel', '0025_merge_20250303_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentinterviewlink',
            name='interview_status',
            field=models.CharField(choices=[('Pass', 'Pass'), ('Fail', 'Fail')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='studentinterviewlink',
            name='overall_score',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='studentinterviewlink',
            name='total_answer_scores',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='studentinterviewlink',
            name='total_grammer_scores',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='studentinterviewlink',
            name='total_sentiment_score',
            field=models.TextField(null=True),
        ),
    ]
