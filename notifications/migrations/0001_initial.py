# Generated by Django 3.2.12 on 2022-02-24 15:41

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=11, unique=True, validators=[django.core.validators.RegexValidator(message='Номер телефона должен быть в формате 7XXXXXXXXXX (X - цифры от 0 до 9)', regex='^7\\d{10}$')])),
                ('utc', models.CharField(max_length=3, validators=[django.core.validators.RegexValidator(message='Часовой пояс должен быть в формате "+3", "-10" или "0" итд', regex='^[+-]?([01]\\d?)|(\\d)')])),
            ],
        ),
        migrations.CreateModel(
            name='Mailing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_datetime', models.DateTimeField()),
                ('text', models.TextField()),
                ('stop_datetime', models.DateTimeField()),
                ('finished_datetime', models.DateTimeField(blank=True, null=True)),
                ('finished', models.BooleanField(default=False)),
                ('expired', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Operator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=3, unique=True, validators=[django.core.validators.RegexValidator(message='Код оператора должен состоять из трёх цифр', regex='^\\d{3}$')])),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_datetime', models.DateTimeField(auto_now_add=True)),
                ('sent_datetime', models.DateTimeField(blank=True, null=True)),
                ('sent', models.BooleanField(default=False)),
                ('client', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='notifications.client')),
                ('mailing', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='notifications.mailing')),
            ],
        ),
        migrations.AddField(
            model_name='mailing',
            name='operators',
            field=models.ManyToManyField(blank=True, related_name='mailings', to='notifications.Operator'),
        ),
        migrations.AddField(
            model_name='mailing',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='mailings', to='notifications.Tag'),
        ),
        migrations.AddField(
            model_name='client',
            name='operator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clients', to='notifications.operator'),
        ),
        migrations.AddField(
            model_name='client',
            name='tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='clients', to='notifications.tag'),
        ),
    ]
