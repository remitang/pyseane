# Generated by Django 4.2.7 on 2023-11-28 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_remove_target_id_email_hashed_target_id_email_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campagne_fish',
            name='url',
            field=models.CharField(max_length=512, null=True),
        ),
    ]
