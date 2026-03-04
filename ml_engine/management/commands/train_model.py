from django.core.management.base import BaseCommand
from ml_engine.train import train_model

class Command(BaseCommand):
    help = 'Trains the complaint classification model'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            default='nb',
            help='ML technique: nb (Naive Bayes), lr (Logistic Regression), rf (Random Forest)'
        )

    def handle(self, *args, **options):
        algo = options['model']
        self.stdout.write(f'Training model using {algo}...')
        try:
            train_model(algorithm=algo)
            self.stdout.write(self.style.SUCCESS(f'Successfully trained and saved models using {algo}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error training model: {e}'))
