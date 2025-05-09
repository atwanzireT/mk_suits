# Generated by Django 5.2 on 2025-04-29 04:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_alter_ordertransaction_customer_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='special_notes',
            field=models.CharField(blank=True, choices=[('nothing', 'Nothing'), ('strongly spiced', 'Strongly Spiced'), ('midly spiced', 'Mildly Spiced'), ('chips', 'Chips'), ('rice', 'Rice'), ('posho', 'Posho'), ('rice_posho', 'Rice + Posho'), ('chips_rice', 'Chips + Rice'), ('chips_posho', 'Chips + Posho')], default='nothing', max_length=50, null=True),
        ),
    ]
