# Generated by Django 3.1.7 on 2021-04-28 08:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20210427_1650'),
    ]

    operations = [
        migrations.CreateModel(
            name='Space',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('devices', models.JSONField()),
                ('stay_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='app.stay_data')),
            ],
        ),
    ]
