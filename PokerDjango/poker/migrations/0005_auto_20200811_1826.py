# Generated by Django 3.1 on 2020-08-11 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poker', '0004_auto_20200810_2326'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='players',
            field=models.ManyToManyField(related_name='games', to='poker.Player'),
        ),
    ]