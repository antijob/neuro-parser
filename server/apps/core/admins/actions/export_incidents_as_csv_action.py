import csv
from django.http import HttpResponse


def export_incidents_as_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="filtered_data.csv"'

    writer = csv.writer(response)

    for obj in queryset:
        writer.writerow([obj.description])

    return response


export_incidents_as_csv.short_description = "Экспортировать выбранные записи в CSV"
