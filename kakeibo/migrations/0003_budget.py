# Generated by Django 4.0.4 on 2022-05-25 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kakeibo', '0002_alter_income_description_alter_payment_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateField(verbose_name='月')),
                ('price', models.IntegerField(verbose_name='予算')),
                ('rest', models.IntegerField(verbose_name='残額')),
            ],
        ),
    ]
