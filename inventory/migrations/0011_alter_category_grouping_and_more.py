# Generated by Django 5.2 on 2025-05-03 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_alter_ordertransaction_created_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='grouping',
            field=models.CharField(choices=[('Appetizers', 'Appetizers'), ('Starter', 'Starter'), ('Main Dishes', 'Main Dishes'), ('Desserts', 'Desserts'), ('Beverages', 'Beverages'), ('Snacks', 'Snacks'), ('Breakfast', 'Breakfast')], max_length=100),
        ),
        migrations.AlterField(
            model_name='ordertransaction',
            name='payment_mode',
            field=models.CharField(choices=[('NO PAYMENT', 'NO PAYMENT'), ('CASH', 'CASH'), ('MOMO PAY', 'MOMO PAY'), ('AIRTEL PAY', 'AIRTEL PAY'), ('INVOICE', 'INVOICE')], default='NO PAYMENT', max_length=50),
        ),
        migrations.AlterField(
            model_name='ordertransaction',
            name='transaction_id',
            field=models.CharField(blank=True, help_text='Transaction ID / Invoice Number', max_length=100, null=True),
        ),
    ]
