# Generated by Django 3.0.4 on 2020-03-13 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0005_auto_20200313_2255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='video',
            field=models.FileField(default='default.jpg', null=True, upload_to='videos/'),
        ),
    ]