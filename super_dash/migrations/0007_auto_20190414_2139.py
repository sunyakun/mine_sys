# Generated by Django 2.1.4 on 2019-04-14 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('super_dash', '0006_auto_20190411_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='algorithm',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='dataset',
            name='config',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='photo',
            name='photo_url',
            field=models.CharField(default='photo.jpg', max_length=255),
        ),
    ]
