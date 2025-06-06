# Generated by Django 5.1.5 on 2025-01-28 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Students',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.IntegerField()),
                ('student_consent', models.IntegerField()),
                ('interview_start_at', models.DateTimeField(auto_now=True)),
                ('answers_scores', models.IntegerField()),
                ('sentiment_score', models.IntegerField()),
                ('recording_file', models.TextField()),
                ('interview_end_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'indexes': [models.Index(fields=['id'], name='studentpane_id_593b17_idx')],
            },
        ),
    ]
