# Generated by Django 5.1.5 on 2025-02-24 11:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0007_book_cover_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='cover_url',
        ),
    ]
