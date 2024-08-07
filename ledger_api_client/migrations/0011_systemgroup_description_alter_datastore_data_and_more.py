# Generated by Django 5.0.7 on 2024-08-07 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledger_api_client', '0010_systemuser_account_change_locked'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemgroup',
            name='description',
            field=models.TextField(blank=True, default='', null=True),
        ),
        migrations.AlterField(
            model_name='datastore',
            name='data',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='emailuser',
            name='ledger_data',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='emailuser',
            name='ledger_groups',
            field=models.JSONField(default=dict),
        ),
    ]
