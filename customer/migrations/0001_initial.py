# Generated by Django 5.0.6 on 2024-10-21 11:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='billing_addr',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(max_length=250)),
                ('state', models.CharField(max_length=250)),
                ('country', models.CharField(max_length=250)),
                ('address', models.CharField(max_length=250)),
            ],
            options={
                'db_table': 'billing_addr',
            },
        ),
        migrations.CreateModel(
            name='customer_incentive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.CharField(max_length=255)),
                ('customer_name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=64)),
                ('initial_amount', models.DecimalField(decimal_places=2, max_digits=64)),
                ('balance', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=64)),
                ('type', models.CharField(default='Credit', max_length=255)),
                ('date', models.DateField()),
                ('token_id', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'db_table': 'customer_incentive',
            },
        ),
        migrations.CreateModel(
            name='customer_invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cusID', models.CharField(max_length=225)),
                ('customer_name', models.CharField(blank=True, max_length=225, null=True)),
                ('invoiceID', models.CharField(blank=True, max_length=225, null=True)),
                ('order_ID', models.CharField(blank=True, max_length=225, null=True)),
                ('Gdescription', models.CharField(max_length=225)),
                ('invoice_date', models.DateTimeField()),
                ('due_date', models.DateField()),
                ('itemcode', models.CharField(max_length=50)),
                ('item_name', models.CharField(blank=True, max_length=200, null=True)),
                ('item_description', models.CharField(blank=True, max_length=225, null=True)),
                ('qty', models.DecimalField(decimal_places=2, default=0.0, max_digits=12)),
                ('unit_p', models.DecimalField(decimal_places=2, max_digits=12)),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('token_id', models.CharField(blank=True, max_length=50)),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=12)),
                ('amount_expected', models.DecimalField(decimal_places=2, max_digits=12)),
                ('cancellation_status', models.CharField(default='0', max_length=50)),
                ('status', models.CharField(default='0', max_length=50)),
                ('Userlogin', models.CharField(blank=True, max_length=50)),
                ('payment_method', models.CharField(blank=True, max_length=50)),
                ('Transfer', models.CharField(default='0', max_length=50)),
                ('POS', models.CharField(default='0', max_length=50)),
                ('Cash', models.CharField(default='0', max_length=50)),
                ('Customer_account', models.CharField(default='0', max_length=50)),
                ('Cheque', models.CharField(default='0', max_length=50)),
                ('invoice_state', models.CharField(max_length=50)),
                ('purchaseP', models.DecimalField(decimal_places=2, max_digits=12)),
                ('total_purchaseP', models.DecimalField(decimal_places=2, max_digits=12)),
                ('outlet', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'customer_invoice',
            },
        ),
        migrations.CreateModel(
            name='customer_table',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('customer_code', models.CharField(max_length=50, unique=True)),
                ('phone', models.CharField(max_length=100, unique=True)),
                ('instant_email', models.CharField(default=1, max_length=10)),
                ('email', models.EmailField(blank=True, max_length=100)),
                ('token_id', models.IntegerField(blank=True, null=True)),
                ('Balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=65)),
                ('invoice', models.IntegerField(blank=True, default=0)),
                ('company_name', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('Whole Sale', 'Whole Sale'), ('Retail', 'Retail')], default='RETAIL', max_length=20)),
                ('refund_invoice', models.IntegerField(blank=True, default=0)),
                ('Userlogin', models.CharField(blank=True, max_length=60, null=True)),
            ],
            options={
                'db_table': 'customer_table',
            },
        ),
        migrations.CreateModel(
            name='deposit_transfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cusID', models.CharField(max_length=256)),
                ('customer_name', models.CharField(max_length=256)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=65)),
                ('prove', models.CharField(default='none', max_length=256)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'deposit_transfer',
            },
        ),
        migrations.CreateModel(
            name='evidentPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_ref', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=64)),
                ('file', models.ImageField(blank=True, max_length=255, null=True, upload_to='payment_proov/')),
                ('description', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'evidentPayment',
            },
        ),
        migrations.CreateModel(
            name='order_invoice_billing_address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=256)),
                ('reference', models.CharField(max_length=256)),
                ('billing_addr', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'order_invoice_billing_address',
            },
        ),
        migrations.CreateModel(
            name='order_invoice_reference_address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=256)),
                ('reference', models.CharField(max_length=256)),
                ('shipping_addr', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'order_invoice_reference_address',
            },
        ),
        migrations.CreateModel(
            name='payable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True, max_length=222)),
                ('description', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=50)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=64)),
                ('initial_amount', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=64)),
                ('balance', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=64)),
                ('vendor_id', models.CharField(blank=True, max_length=50)),
                ('vendor_name', models.CharField(blank=True, max_length=60)),
                ('payment_method', models.CharField(max_length=50)),
                ('cur_datetime', models.DateTimeField(auto_now_add=True)),
                ('account_posted', models.CharField(blank=True, max_length=50)),
                ('transaction_id', models.CharField(blank=True, max_length=50)),
                ('transaction_source', models.CharField(blank=True, default=0, max_length=200)),
                ('token_id', models.CharField(blank=True, max_length=50)),
                ('Userlogin', models.CharField(blank=True, max_length=50)),
            ],
            options={
                'db_table': 'payable',
            },
        ),
        migrations.CreateModel(
            name='receivable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('description', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=64)),
                ('initial_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=64, null=True)),
                ('balance', models.DecimalField(blank=True, decimal_places=2, max_digits=64, null=True)),
                ('customer_id', models.CharField(blank=True, max_length=50)),
                ('customer_name', models.CharField(blank=True, max_length=60)),
                ('payment_method', models.CharField(max_length=50)),
                ('cur_datetime', models.DateTimeField(auto_now_add=True)),
                ('account_posted', models.CharField(blank=True, max_length=50)),
                ('transaction_id', models.CharField(blank=True, max_length=50)),
                ('token_id', models.CharField(blank=True, max_length=50)),
                ('Userlogin', models.CharField(blank=True, max_length=50)),
                ('invoice_status', models.CharField(max_length=200)),
            ],
            options={
                'db_table': 'receivable',
            },
        ),
        migrations.CreateModel(
            name='sales_order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genby', models.CharField(max_length=20)),
                ('order_ID', models.CharField(blank=True, default='9255977', max_length=50, null=True)),
                ('referenceID', models.CharField(blank=True, max_length=50, null=True)),
                ('Gdescription', models.CharField(blank=True, max_length=225, null=True)),
                ('order_date', models.DateField()),
                ('itemcode', models.CharField(max_length=50)),
                ('item_name', models.CharField(blank=True, max_length=200, null=True)),
                ('item_description', models.CharField(blank=True, max_length=225, null=True)),
                ('qty', models.IntegerField(blank=True, null=True)),
                ('unit_p', models.DecimalField(decimal_places=2, max_digits=12)),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('token_id', models.CharField(blank=True, max_length=50, null=True)),
                ('custID', models.CharField(blank=True, max_length=50, null=True)),
                ('Userlogin', models.CharField(blank=True, max_length=60, null=True)),
            ],
            options={
                'db_table': 'sales_order',
            },
        ),
        migrations.CreateModel(
            name='sales_quote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genby', models.CharField(max_length=20)),
                ('quote_ID', models.CharField(blank=True, default='2388960', max_length=50, null=True)),
                ('referenceID', models.CharField(blank=True, max_length=50, null=True)),
                ('Gdescription', models.CharField(blank=True, max_length=225, null=True)),
                ('quote_date', models.DateField()),
                ('itemcode', models.CharField(blank=True, max_length=50, null=True)),
                ('item_name', models.CharField(blank=True, max_length=200, null=True)),
                ('item_description', models.CharField(blank=True, max_length=225, null=True)),
                ('qty', models.IntegerField(blank=True, null=True)),
                ('unit_p', models.DecimalField(blank=True, decimal_places=2, max_digits=60, null=True)),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('total', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('token_id', models.CharField(blank=True, max_length=50, null=True)),
                ('custID', models.CharField(blank=True, max_length=50, null=True)),
                ('Userlogin', models.CharField(blank=True, max_length=60, null=True)),
            ],
            options={
                'db_table': 'sales_qoute',
            },
        ),
        migrations.CreateModel(
            name='sales_return',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('genby', models.CharField(max_length=200)),
                ('cusID', models.CharField(max_length=200)),
                ('invoiceID', models.CharField(max_length=255)),
                ('refrence_ID', models.CharField(max_length=255)),
                ('Gdescription', models.CharField(max_length=255)),
                ('refund_date', models.DateField(auto_now_add=True, max_length=222)),
                ('itemcode', models.CharField(max_length=255)),
                ('item_name', models.CharField(max_length=255)),
                ('item_description', models.CharField(max_length=255)),
                ('qty', models.DecimalField(blank=True, decimal_places=2, max_digits=64, null=True)),
                ('unit_p', models.DecimalField(blank=True, decimal_places=2, max_digits=64, null=True)),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=64, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=64, null=True)),
                ('token_id', models.CharField(blank=True, max_length=255)),
                ('amount_paid', models.DecimalField(blank=True, decimal_places=2, max_digits=64, null=True)),
                ('amount_expected', models.DecimalField(blank=True, decimal_places=2, max_digits=64, null=True)),
                ('cur_date', models.DateTimeField(auto_now_add=True)),
                ('Userlogin', models.CharField(blank=True, max_length=60)),
            ],
            options={
                'db_table': 'sales_return',
            },
        ),
        migrations.CreateModel(
            name='Vat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'vat',
            },
        ),
    ]