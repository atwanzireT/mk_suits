# Generated by Django 5.1.5 on 2025-05-06 12:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0013_expense_drawn_by_alter_expense_description'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Expense',
        ),
    ]
