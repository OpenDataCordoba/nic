# Generated by Django 3.1.2 on 2021-01-08 23:36

from django.db import migrations, models, transaction
import uuid


def gen_uuid(apps, schema_editor, model_real_name):
    MyModel = apps.get_model('dominios', model_real_name)
    c = 0
    while MyModel.objects.filter(uid__isnull=True).exists():
        c += 1
        print('model_real_name: {} = {} - {}'.format(model_real_name, c, MyModel.objects.filter(uid__isnull=True).count()))
        with transaction.atomic():
            for row in MyModel.objects.filter(uid__isnull=True)[:1000]:
                row.uid = uuid.uuid4()
                row.save(update_fields=['uid'])


def update_dnsdominios(apps, schema_editor):
    gen_uuid(apps, schema_editor, model_real_name='DNSDominio')


def update_dominios(apps, schema_editor):
    gen_uuid(apps, schema_editor, model_real_name='Dominio')


def update_predominios(apps, schema_editor):
    gen_uuid(apps, schema_editor, model_real_name='PreDominio')


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dominios', '0013_auto_20201128_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='dnsdominio',
            name='uid',
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(update_dnsdominios, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='dnsdominio',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),

        migrations.AddField(
            model_name='dominio',
            name='uid',
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(update_dominios, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='dominio',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),

        migrations.AddField(
            model_name='predominio',
            name='uid',
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(update_predominios, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='predominio',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        
    ]
