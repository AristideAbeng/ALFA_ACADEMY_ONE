# Generated by Django 4.2.16 on 2024-09-18 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Payment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='payment_method',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
