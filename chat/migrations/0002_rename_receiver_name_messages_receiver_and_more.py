# Generated by Django 4.2.4 on 2023-10-31 16:40

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="messages",
            old_name="receiver_name",
            new_name="receiver",
        ),
        migrations.RenameField(
            model_name="messages",
            old_name="sender_name",
            new_name="sender",
        ),
    ]
