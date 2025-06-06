# adminpanel/management/commands/create_structure.py

from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Creates a basic structure for models, views, and URLs'

    def handle(self, *args, **kwargs):
        app_dir = 'adminpanel'  # Change this to your app name
        directories = [
            os.path.join(app_dir, 'models'),
            os.path.join(app_dir, 'views'),
            os.path.join(app_dir, 'urls'),
        ]

        files = [
            # models
            os.path.join(app_dir, 'models', 'auth.py'),
            os.path.join(app_dir, 'models', 'user.py'),
            os.path.join(app_dir, 'models', 'institute.py'),
            os.path.join(app_dir, 'models', 'course.py'),
            os.path.join(app_dir, 'models', 'question.py'),
            os.path.join(app_dir, 'models', 'common_question.py'),
            os.path.join(app_dir, 'models', 'student_manager.py'),
            os.path.join(app_dir, 'models', 'student_manager_profile.py'),


            # views
            os.path.join(app_dir, 'views', 'dashboard_view.py'),
            os.path.join(app_dir, 'views', 'auth_view.py'),
            os.path.join(app_dir, 'views', 'institute_view.py'),
            os.path.join(app_dir, 'views', 'course_view.py'),
            os.path.join(app_dir, 'views', 'question_view.py'),
            os.path.join(app_dir, 'views', 'student_manager_view.py'),
        ]

        # Create directories if they don't exist
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)

        # Create empty files if they don't exist
        for file in files:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    f.write('')

        self.stdout.write(self.style.SUCCESS('Successfully created the structure!'))
