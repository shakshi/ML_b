# Generated by Django 3.0.4 on 2020-03-14 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0006_auto_20200313_2256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='video',
            field=models.FileField(default=None, null=True, upload_to='videos/'),
        ),
    ]