# Generated by Django 3.1.5 on 2021-03-06 19:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20210306_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='notifications',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications_id', to='accounts.notification'),
        ),
    ]
