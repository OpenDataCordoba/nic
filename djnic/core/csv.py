import csv
import os
import time
from http import HTTPStatus
from django.conf import settings
from django.http import HttpResponse, FileResponse
from analytics.models import Analytic


def queryset_as_csv_view(request, filename, queryset, fields, override_fields={}, cache_seconds=86400 * 30):
    """ create a CSV to download
        queryset: could be a queryset or a list of dicts (using .values('field1', 'field2'))
        fields: real fields in queryset
        override_fields: optional, give nice names to fields {'ugly__name': 'Nice Name'}
        """

    user = None if request.user.is_anonymous else request.user
    Analytic.objects.create(
        evento='download',
        user=user,
        referencia=filename,
        extras=Analytic.request_as_dict(request)
    )

    if user is None:
        return HttpResponse('Descarga habilitada para usuarios registrados', status=HTTPStatus.NO_CONTENT)

    # revisar la carpata de descargas
    # ver si la ultima grabacion está dentro del tiempo de cache
    if not os.path.isdir(settings.DOWNLOADS_ROOT):
        os.makedirs(settings.DOWNLOADS_ROOT)

    full_path = os.path.join(settings.DOWNLOADS_ROOT, filename)
    file_ready = False
    if os.path.isfile(full_path):
        file_age = time.time() - os.path.getmtime(full_path)
        if file_age > cache_seconds:
            os.remove(full_path)
        else:
            file_ready = True

    if not file_ready:
        if queryset.count() == 0:
            return HttpResponse(f'No data for {filename}', status=HTTPStatus.NO_CONTENT)

        csvf = open(full_path, 'w')
        # obtener los nombres mejorados de las columnas
        fixed_fields = {}
        for f in fields:
            fixed_fields[f] = override_fields.get(f, f)

        # imprimir las columnas
        writer = csv.DictWriter(csvf, fieldnames=fixed_fields.values())
        writer.writeheader()

        for row in queryset:
            if type(row) == dict:
                final_row = {fixed_fields[k]: row[k] for k in fields}
            else:
                final_row = {fixed_fields[k]: getattr(row, k) for k in fields}
            writer.writerow(final_row)

    return FileResponse(open(full_path, 'rb'))
