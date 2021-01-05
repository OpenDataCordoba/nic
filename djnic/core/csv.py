import csv
from http import HTTPStatus
from django.http import HttpResponse


def queryset_as_csv_view(filename, queryset, fields, override_fields={}):
    """ create a CSV to download
        queryset: could be a queryset or a list of dicts (using .values('field1', 'field2'))
        fields: real fields in queryset
        override_fields: optional, give nice names to fields {'ugly__name': 'Nice Name'}
        """

    # TODO save analytics from downloads

    if queryset.count() == 0:
        return HttpResponse(f'No data for {filename}', status=HTTPStatus.NO_CONTENT)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # obtener los nombres mejorados de las columnas
    fixed_fields = {}
    for f in fields:
        fixed_fields[f] = override_fields.get(f, f)

    # imprimir las columnas
    writer = csv.DictWriter(response, fieldnames=fixed_fields.values())
    writer.writeheader()

    for row in queryset:
        if type(row) == dict:
            final_row = {fixed_fields[k]: row[k] for k in fields}
        else:
            final_row = {fixed_fields[k]: getattr(row, k) for k in fields}
        writer.writerow(final_row)

    return response
