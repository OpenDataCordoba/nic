# Generated by Django 3.1.2 on 2020-10-12 05:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dnss', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dns',
            name='dominio',
            field=models.CharField(max_length=240, unique=True),
        ),
    ]