# Generated by Django 5.1.5 on 2025-05-06 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0014_delete_expense'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(max_length=200)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateField()),
                ('drawn_by', models.CharField(default='staff', max_length=30)),
                ('category', models.CharField(max_length=50)),
            ],
        ),
    ]
