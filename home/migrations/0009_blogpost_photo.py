# Generated by Django 4.1.10 on 2023-07-20 06:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_customuser_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogpost',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='blog_photos/'),
        ),
    ]
