# Generated by Django 5.0.6 on 2024-10-23 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor_invoice',
            name='cusID',
            field=models.CharField(blank=True, default='9042346', max_length=25),
        ),
        migrations.AlterField(
            model_name='vendor_invoice',
            name='token_id',
            field=models.CharField(blank=True, default='BNARTqJ7ej', max_length=255),
        ),
        migrations.AlterField(
            model_name='vendor_order',
            name='custID',
            field=models.CharField(blank=True, default='UmPf41IN4e', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_order',
            name='order_ID',
            field=models.CharField(blank=True, default='3732411', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_order',
            name='token_id',
            field=models.CharField(blank=True, default='7783789', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_quote',
            name='custID',
            field=models.CharField(blank=True, default='btzJn1lymB', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_quote',
            name='quote_ID',
            field=models.CharField(blank=True, default='1195613', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_quote',
            name='token_id',
            field=models.CharField(blank=True, default='9818724', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_return',
            name='cusID',
            field=models.CharField(blank=True, default='j4wrmDpRxa', max_length=255),
        ),
        migrations.AlterField(
            model_name='vendor_return',
            name='token_id',
            field=models.CharField(blank=True, default='5496496', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='vendor_table',
            name='address',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='vendor_table',
            name='email',
            field=models.EmailField(blank=True, error_messages={'unique': 'Your email must be unique'}, max_length=150, unique=True),
        ),
    ]