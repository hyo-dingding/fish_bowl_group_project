# Generated by Django 5.1 on 2024-08-26 14:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("llm", "0002_file_data_uploaded_at"),
    ]

    operations = [
        migrations.RenameField(
            model_name="file_data",
            old_name="file_field",
            new_name="file",
        ),
    ]
