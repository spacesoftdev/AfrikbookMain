from customer.forms import CustomerSalesForm, ReceivableForm, PayableForm
from customer.models import customer_table, customer_invoice, receivable, payable, Vat #CreateOutletStockIn, CreateOutletStockInLog, 
from vendor.models import vendor_table, Vendor_invoice
from account.models import *
from Stock.models import CreateOutletStockIn, CreateOutletStockInLog
from django.contrib import messages
import decimal
import uuid
from Stock.models import Item
from customer.utils import generate_order_id
from main.models import User
from customer.functions.generalFunction import *
from django.http import JsonResponse
from datetime import datetime
from settings.models import shipping_cost

def invoiceExist(request, invoiceID):
    db = request.user.company_id.db_name
    # check if invoice number exists          
    if customer_invoice.objects.using(db).filter(invoiceID=invoiceID).exists() or Vendor_invoice.objects.using(db).filter(invoiceID=invoiceID).exists():
        return JsonResponse(True, safe=False)
    else:
        return JsonResponse(False, safe=False)
    
def billing_shipping_address(request, name):
    shipping = request.POST.get('shipping_address')
    method = request.POST.get('shipping_method')
    if shipping and method:
        return True
    else:
        # messages.error(request, name+" has no Shipping and Billing address")
        return False   
    
    
def billing_shipping_reference(db, invoice, cusID, shipping, method, cost):
    
    try:
        order_invoice_reference_address.objects.using(db).get(reference=invoice)
    except order_invoice_reference_address.DoesNotExist:
        order_invoice_reference_address.objects.using(db).create(source=method, reference=invoice, shipping_addr=shipping) 
   # order_invoice_billing_address.objects.using(db).create(source="", reference=invoice, billing_addr=billing) 
        
    try:
       shipping_cost.objects.using(db).get(invoiceID=invoice)
    except shipping_cost.DoesNotExist:
        shipping_cost.objects.using(db).create(invoiceID=invoice, amount=cost, custID=cusID)
        
    


def add_new_sales(request, db):
    
    message_displayed = False  # Initialize the message_displayed variable
    executed = False  
    user = False  
   
    cusID             = request.POST['cusID']
    venID             = request.POST['venID']
    acountType        = request.POST['accountType']
    customer_name     = request.POST['genby']
    invoice_date      = request.POST['invoice_date']
    due_date          = request.POST['due_date']
    invoiceID         = request.POST['invoiceID']
    order_id          = request.POST['order_id']
    Gdescription      = request.POST['Gdescription']
    invoice_state     = request.POST.get('invoice_state')
    credit_sales      = request.POST.get('credit_sales')
    item_name         = request.POST.getlist('item_name')
    purchaseP         = request.POST.getlist('purchaseP')
    itemcode          = request.POST.getlist('item[]')
    item_descriptions = request.POST.getlist('desc[]')
    quantities        = request.POST.getlist('qty[]')
    unit              = request.POST.getlist('unit[]')
    discount          = request.POST.getlist('discount[]')
    amount            = request.POST.getlist('amount[]')
    vat               = request.POST.get('vat') #[:-1]
    sub_total         = request.POST['sub-total']
    total             = request.POST['total']
    account_ID = request.POST.get('t_account')
    transfer = request.POST.get('transfer_amount')
    cash = request.POST.get('cash_amount')
    payment_method = request.POST.get('payment_method')
    method = request.POST.get('shipping_method')
    shipping = request.POST.get('shipping_address')
    shipping_cost = request.POST.get('shipping_cost')

    instant_stockout = request.session.get('IN_STOCKOUT', 'Yes')
    
    
    if instant_stockout == "Yes":
        status = 1
    else:
        status = 0
  
    if invoice_state:
        invoice_state = "Pending"
    else:
        invoice_state = "Supplied"
    
    # Note if any changes in this statement you have to make same chabges on return inward function
    if credit_sales:
        amount_paid = 0.00
        amount_expected = total
    else:
        amount_paid = total
        amount_expected = total

    # amount_paid = total
    # amount_expected = sub_total
    
    
    
    int_purchaseP = [int(num) if num.isdigit() else 0 for num in purchaseP ]

    total_purchaseP = sum(int_purchaseP)

    if cusID:
        res = billing_shipping_address(request, customer_name)    
        customer_code = customer_table.objects.using(db).get(id=cusID).customer_code

    elif venID:
        res = False
        customer_code = vendor_table.objects.using(db).get(id=venID).custID
    else:        
        customer_code = None

    
    date_ = datetime.strptime(invoice_date, "%Y-%m-%d").date()
    current_time = datetime.now().time()

    date_time = datetime.combine(date_, current_time)
   
    for i in range(len(itemcode)):
            # Check if the itemcode (value) is equal to 0
        if i < len(itemcode) and str(itemcode[i]) != "0":
             # Check if quantity (value) is equal to 0 or empty 
            if not quantities[i] or int(quantities[i]) == 0:
                #Automatically change the quantity to 1
                quantities[i] = 1
        
            form_data = {
                'cusID': customer_code,
                'customer_name':customer_name,
                'invoice_date':date_time,
                'due_date': due_date,
                'invoiceID':invoiceID ,
                'order_ID':order_id ,
                'Gdescription': Gdescription,
                'item_name': item_name[i],
                'itemcode': itemcode[i],
                'item_description': item_descriptions[i],
                'qty': quantities[i],
                'unit_p': unit[i],
                'discount': discount[i],
                'amount': amount[i],
                'amount_paid': amount_paid,
                'amount_expected': amount_expected,

                "cancellation_status":0,
                "status":status,
                "Transfer":0,
                "POS":0,
                "Cash":0,
                "Customer_account":0,
                "Cheque":0,
                "invoice_state":invoice_state,
                "purchaseP":purchaseP[i],
                "total_purchaseP":total_purchaseP,
                "outlet": request.user.outlet
            }
            cus_form = CustomerSalesForm(form_data)
      
            receivable_form = ReceivableForm({"date":invoice_date,	"description":Gdescription,"type": "Debit",	"amount": amount_paid, "payment_method": "Transfer","account_posted":"","invoice_status": "Unused"})
            
                
            if cus_form.is_valid() and receivable_form.is_valid():
                form  = cus_form.save(commit=False)
                form.Userlogin = request.user.username
                form.save(using=db)
                print(db)
                #Reduce stock quantity
                if invoice_state == "Supplied":
                    outlet= request.user.outlet
                    # print(item_name[i])
                    ReduceOutletStockinItemQuantity(db, outlet, itemcode[i], quantities[i])

                if not message_displayed:
                    if acountType == "Customer":
                        cus = customer_table.objects.using(db).get(id=cusID)
                        cus.invoice = cus.invoice + 1
                        cus.save()
                        
                    elif acountType == "Vendor":
                        ven = vendor_table.objects.using(db).get(id=venID)
                        ven.invoices = int(ven.invoices) + 1
                        ven.save()
                    if credit_sales == None:
                        # insert into recievable
                        if account_ID:
                            account = chart_of_account.objects.using(db).get(account_id=account_ID)
                            if acountType == "Customer":
                                DebitReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account_ID, total)  
                            elif acountType == "Vendor":
                                DebitPayable(request, db, ven, invoice_date, Gdescription, payment_method, account_ID, total) 
                            
                            
                            if payment_method == "Transfer":
                                if acountType == "Customer":
                                    CreditReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account_ID, total)
                                elif acountType == "Vendor":
                                    CreditPayable(request, db, ven, invoice_date, Gdescription, payment_method, account_ID, total)
                                CreateLog(db, account, total) 
                               

                            elif payment_method == "Transfer and Cash":
                                # Transfer 
                                if acountType == "Customer":
                                   CreditReceivable(request, db, cus, invoice_date, Gdescription, "Transfer", account_ID, transfer)
                                elif acountType == "Vendor":
                                    CreditPayable(request, db, cus, invoice_date, Gdescription, "Transfer", account_ID, transfer)
                                CreateLog(db, account, transfer)
                                # Cash
                                cash_account = chart_of_account.objects.using(db).get(account_bankname="Sales account")
                                if acountType == "Customer":
                                   CreditReceivable(request, db, cus, invoice_date, Gdescription, "Cash", cash_account.account_id, cash)
                                elif acountType == "Vendor":
                                    CreditPayable(request, db, cus, invoice_date, Gdescription, "Cash", cash_account.account_id, cash)
                                CreateLog(db, cash_account, cash)

                            elif payment_method == "Cheque":
                                account = chart_of_account.objects.using(db).get(account_bankname="Account Receivable")     
                                CreateLog(db, account, total)
                            else:
                                account = chart_of_account.objects.using(db).get(account_bankname="Sales account")
                                if acountType == "Customer":
                                    CreditReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account.account_id, total)
                                elif acountType == "Vendor":
                                    CreditPayable(request, db, ven, invoice_date, Gdescription, payment_method, account.account_id, total)
                                   
                                CreateLog(db, account, total)

                        else:
                            if acountType == "Customer":
                                account = chart_of_account.objects.using(db).get(account_bankname="Sales account")
                                DebitReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account.account_id, total)
                                CreditReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account.account_id, total)
                                CreateLog(db, account, total)
                            elif acountType == "Vendor":
                                account = chart_of_account.objects.using(db).get(account_bankname="Sales account")
                                DebitPayable(request, db, ven, invoice_date, Gdescription, payment_method, account.account_id, total)
                                CreditPayable(request, db, ven, invoice_date, Gdescription, payment_method, account.account_id, total) 
                                CreateLog(db, account, total)
  
                    else:
                        if acountType == "Customer":
                            account = chart_of_account.objects.using(db).get(account_bankname="Sales account")
                            account.actual_balance += decimal.Decimal(total)
                            # account.save()
                            DebitReceivable(request, db, cus, invoice_date, Gdescription, payment_method, account.account_id, total)
                            CreateLog(db, account, total)
                        elif acountType == "Vendor":
                            account = chart_of_account.objects.using(db).get(account_bankname="Purchase account")
                            account.actual_balance += decimal.Decimal(total)
                            # account.save()
                            DebitPayable(request, db, ven, invoice_date, Gdescription, payment_method, account.account_id, total)
                            CreateLog(db, account, total)
                        
                        acc_log = account_log(
                                transaction_source  = "Sales",
                                amount              = total,
                                date                = invoice_date,
                                account             = account.account_id,
                                account_type        = account.account_type,
                                Userlogin = request.user.username
                            )
                        # acc_log.save(using=db)

                    if res:
                        billing_shipping_reference(db, invoiceID, cusID, shipping, method, shipping_cost)
                    else:
                        pass
                    create_add_vat(db, invoiceID, vat)

                    messages.success(request, "New Sales Invoice was added successfully")
                    message_displayed = True
            else:
                # print("Customer form error", cus_form.errors)
                # print("Receivable form error", receivable_form.errors)
                return cus_form
        elif len(itemcode) == 1 and itemcode[i] == "0":
            if not executed:
                messages.error(request, "Select at least one item")
                executed = True
   


def create_add_vat(db, invoiceID, vat):
    # print(db, invoiceID, vat)
    if vat:
        try:
            Vat.objects.using(db).get(source=invoiceID, amount=vat)
        except Vat.DoesNotExist:
            Vat.objects.using(db).create(source=invoiceID, amount=vat)
            vat_account = chart_of_account.objects.using(db).get(account_bankname="Vat Account")
            vat_account.actual_balance += decimal.Decimal(vat)
            vat_account.save()

def create_minus_vat(db, invoiceID, vat):
    
    if vat:
        try:
            Vat.objects.using(db).get(source=invoiceID, amount=-abs(decimal.Decimal(vat)))
        except Vat.DoesNotExist:
            Vat.objects.using(db).create(source=invoiceID, amount=-abs(decimal.Decimal(vat)))
            vat_account = chart_of_account.objects.using(db).get(account_bankname="Vat Account")
            vat_account.actual_balance -= decimal.Decimal(vat)
            vat_account.save()