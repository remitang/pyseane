# Generated by Django 4.2.7 on 2023-11-28 08:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_target'),
    ]

    operations = [
        migrations.AlterField(
            model_name='target',
            name='id_email_hashed',
            field=models.CharField(max_length=65, primary_key=True, serialize=False),
        ),
    ]
