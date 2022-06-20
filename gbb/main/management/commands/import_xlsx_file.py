from zipfile import BadZipFile

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from gbb.main.constants import COMMA
from gbb.main.models import Competitor
from gbb.main.models import Product


class Command(BaseCommand):
    help = "Import XLSX file to database"
    missing_args_message = "File must set by --file parametr"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file", help="path to xlsx file", nargs=1, required=True, type=str
        )

    def _get_worksheet(self, file_path):
        try:
            workbook = load_workbook(filename=file_path)
            worksheet = workbook.worksheets[0]
        except InvalidFileException as e:
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
            quit()
        except BadZipFile as e:
            self.stdout.write(
                self.style.ERROR(f"Error: bad format of file {file_path}. Error: {e}")
            )
            quit()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"File {file_path} open problem: {e}"))
            quit()
        return worksheet

    def _str_to_pricing_strategy(self, src_str):
        src_str = src_str.strip().upper()
        if src_str == Product.PricingStrategy.AVERAGE.value:
            return Product.PricingStrategy.AVERAGE
        if src_str == Product.PricingStrategy.EDLP.value:
            return Product.PricingStrategy.EDLP
        raise ValueError("Cant cast type")

    def _get_list_competitor(self, src_str):
        src_str = src_str.strip()
        if COMMA in src_str:
            return [s.strip() for s in src_str.split(COMMA)]
        return [
            src_str,
        ]

    def _process_competitor(self, worksheet, number, product):
        competitors_str = worksheet[f"C{number}"].value
        if competitors_str is None:
            return
        if competitors_str == "":
            return
        if product is None:
            return
        competitors_ids = self._get_list_competitor(competitors_str)
        for competitor in competitors_ids:
            Competitor.objects.create(product=product, article=competitor)

    def _process_line(self, worksheet, number):
        if number == 1:
            return  # Пропускаем заголовок таблицы
        article = worksheet[f"A{number}"].value.strip()
        if article is None:
            return None
        if article == "":
            return None
        product = Product.objects.create(
            article=article,
            pricing_strategy=self._str_to_pricing_strategy(
                worksheet[f"B{number}"].value
            ),
        )
        return product

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Start"))
        file_path = options["file"][0]
        worksheet = self._get_worksheet(file_path)
        self.stdout.write(self.style.SUCCESS(f"File: {file_path}"))
        vertical_cursor = 1
        while worksheet[f"A{vertical_cursor}"].value is not None:
            try:
                product = self._process_line(worksheet, vertical_cursor)
            except (ValueError, IntegrityError) as e:
                self.stdout.write(self.style.ERROR(f"Error: {e}"))
                vertical_cursor = vertical_cursor + 1
                continue
            self._process_competitor(worksheet, vertical_cursor, product)
            vertical_cursor = vertical_cursor + 1
        self.stdout.write(self.style.SUCCESS("Complete"))
