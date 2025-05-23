# Generated by Django 5.1.7 on 2025-03-07 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Giocatore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('ruolo', models.CharField(max_length=50)),
                ('squadra', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Partita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('squadra_casa', models.CharField(max_length=100)),
                ('squadra_trasferta', models.CharField(max_length=100)),
                ('arbitro', models.CharField(max_length=100)),
                ('data', models.DateTimeField()),
            ],
        ),
    ]
