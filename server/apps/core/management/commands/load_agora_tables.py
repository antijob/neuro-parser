# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import URLValidator
from openpyxl import load_workbook

from server.apps.core.logic.grabber.region import region_code
from server.apps.core.models import MediaIncident

DATA_DIR = "server/apps/core/management/commands/data/"
ADMINISTRATIVE_TITLES = {
    "default": (
        "Преследование по статье о распространении недостоверной "
        "информации по ч.9 ст.13.15 КоАП РФ"
    ),
    "colored": (
        "Преследование представителей СМИ по статье о распространении "
        "недостоверной информации по ч.9 ст.13.15 КоАП РФ"
    ),
}
CRIMINAL_TITLES = {
    "default": (
        "Преследование по статье о распространении ложной "
        "информации по ст.207.1 УК РФ РФ"
    ),
    "colored": (
        "Уголовное преследование журналистов или политических активистов "
        "по статье о распространении ложной информации 207.1 УК РФ"
    ),
}


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.load_data_from_file(
            "Факты преследований за распространение фейков адм v2.xlsx",
            category=2,
            colored_row_id=0,
            titles=ADMINISTRATIVE_TITLES,
        )
        self.load_data_from_file(
            "Факты преследований за распространение фейков уголов v2.xlsx",
            category=1,
            colored_row_id=2,
            titles=CRIMINAL_TITLES,
        )

    def load_data_from_file(self, filename, category=0, colored_row_id=0, titles=None):
        file_path = DATA_DIR + filename
        cnt = 1
        for row in self.get_rows(file_path):
            cnt += 1
            url1 = (row[6].hyperlink and row[6].hyperlink.target) or row[6].value
            url2 = (row[4].hyperlink and row[4].hyperlink.target) or row[4].value
            url3 = (row[5].hyperlink and row[5].hyperlink.target) or row[5].value
            url = self.valid_url(url1) or self.valid_url(url2) or self.valid_url(url3)
            if not url or self.exists(url):
                continue
            region = region_code(row[0].value)

            color = row[colored_row_id].fill.start_color.index
            if color == "00000000":
                text = titles["default"]
            else:
                text = titles["colored"]

            date_value = row[1].value or row[2].value or row[3].value
            if not date_value:
                continue
            date = date_value.date()
            MediaIncident.objects.create(
                title=text,
                description=text,
                public_title=text,
                public_description=text,
                urls=[url],
                region=region,
                status=MediaIncident.PROCESSED_AND_ACCEPTED,
                incident_type=category,
                count=1,
                create_date=date,
            )

    def get_rows(self, file_path):
        book = load_workbook(file_path)
        sheet = book.active
        for row in list(sheet.rows)[1:]:
            yield row

    def exists(self, url):
        return MediaIncident.objects.filter(urls__contains=[url]).exists()

    @staticmethod
    def valid_url(url):
        if not url:
            return False
        url = url.lstrip('=HYPERLINK("').rstrip('")')
        val = URLValidator()
        try:
            val(url)
            return url
        except ValidationError:
            return False
