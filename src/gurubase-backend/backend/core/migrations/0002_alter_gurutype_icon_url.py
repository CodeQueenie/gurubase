# Generated by Django 4.2.13 on 2024-12-20 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gurutype',
            name='icon_url',
            field=models.CharField(blank=True, default='', max_length=2000, null=True),
        ),
    ]
