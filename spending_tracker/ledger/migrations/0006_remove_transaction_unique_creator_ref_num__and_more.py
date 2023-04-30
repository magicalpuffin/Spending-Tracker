# Generated by Django 4.2 on 2023-04-30 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ledger', '0005_alter_transaction_ref_num_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='transaction',
            name='unique creator ref_num ',
        ),
        migrations.AddConstraint(
            model_name='transaction',
            constraint=models.UniqueConstraint(fields=('creator', 'ref_num'), name='unique transaction creator ref_num '),
        ),
        migrations.AddConstraint(
            model_name='type',
            constraint=models.UniqueConstraint(fields=('creator', 'name'), name='unique type creator name '),
        ),
    ]
