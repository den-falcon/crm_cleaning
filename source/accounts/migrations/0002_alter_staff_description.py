# Generated by Django 4.0.5 on 2022-06-25 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='description',
            field=models.TextField(default=1, max_length=2000, verbose_name='Примечание'),
            preserve_default=False,
        ),
    ]
