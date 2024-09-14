import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand
from progress.bar import IncrementalBar

from recipes.models import Ingredient


def ingredient_create(row):
    try:
        Ingredient.objects.get_or_create(
            name=row[0].strip(),
            measurement_unit=row[1].strip()
        )
    except Exception as e:
        print(f"Error creating ingredient {row}: {e}")


class Command(BaseCommand):
    help = "Load ingredients to DB"

    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, 'ingredients.csv')

        try:
            with open(path, 'r', encoding='utf-8') as file:
                reader = list(csv.reader(file))
                row_count = len(reader) - 1
                bar = IncrementalBar('ingredients.csv'.ljust(17),
                                     max=row_count)
                for row in reader[1:]:
                    if len(row) < 2 or not row[0] or not row[1]:
                        continue
                    bar.next()
                    ingredient_create(row)
                bar.finish()
            self.stdout.write(
                self.style.SUCCESS(
                    'The ingredients have been loaded successfully.'
                )
            )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    'File not found. Please check the path.'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'An error occurred: {e}'
                )
            )
