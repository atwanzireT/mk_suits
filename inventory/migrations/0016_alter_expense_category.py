# Generated by Django 5.1.5 on 2025-05-07 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0015_expense'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='category',
            field=models.CharField(choices=[('Salaries', 'Salaries'), ('Wages', 'Wages'), ('Utilities', 'Utilities'), ('Rs $ M', 'Repairs $ Maintenance'), ('Cleaning $ Laundry Supplies', 'Cleaning $ Laundry Supplies'), ('Others', 'Others')], max_length=30),
        ),
    ]
