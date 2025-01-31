from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        app_dir = "studentpanel"

        # Define the directories
        directories = [
            os.path.join(app_dir, "models"),
            os.path.join(app_dir, "views"),
            os.path.join(app_dir, "urls"),
        ]

        # Define the files
        files = [
            os.path.join(app_dir, "models", "interview_process_model.py"),  # Model file
            os.path.join(app_dir, "views", "interview_process.py"),  # View file
        ]

        # Create directories if they don't exist
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)

        # Create empty files if they don't exist
        for file in files:
            if not os.path.exists(file):
                with open(file, "w") as f:
                    f.write("")

        self.stdout.write(self.style.SUCCESS("Successfully created the structure!"))
