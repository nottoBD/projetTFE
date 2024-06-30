# Generated by Django 5.0.3 on 2024-06-27 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Payments', '0002_paymentcategory_paymentdocument_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentcategory',
            name='type',
            field=models.CharField(choices=[('medical', 'Médicale'), ('schooling', 'Scolarité'), ('child development', 'Développement enfant'), ('other', 'Autre')], default=10, max_length=20),
            preserve_default=False,
        ),
    ]