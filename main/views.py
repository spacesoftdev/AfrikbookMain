from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages 
from customer.models import customer_table, customer_invoice
from customer.functions.newsales import ReduceOutletStockinItemQuantity

from django.contrib.auth import authenticate, login, logout


from .forms import LoginForm, UserRegistrationForm, NewUserForm, PrivilegeForm, PagesForm, UserSettingsForm
from .models import User, Privilege, Pages,   currency
from django.contrib.auth.decorators import login_required
from routers.page_permission import urls_name
from django.views.decorators.cache import never_cache
from .decorators import not_logged_in_required
from account.models import *
from vendor.models import *
from customer.forms import *
from customer.utils import generate_order_id
from main.functions.company.company import *

import json, decimal
from datetime import date
from django.http.response import JsonResponse
from django.views.decorators.http import require_POST 

from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.csrf import csrf_exempt

# from stock.models import Item, Category
from .models import *
from Stock.models import *
from Stockin.models import *
from Stockin.utils import *
from settings.models import sales_outlet, ExpiryDate
from settings.Forms.profile import ProfileSetupForm
from employee.models import employee

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.utils import timezone
from datetime import date
from django.db.models import Sum, Q
from.utils import pagenation



@never_cache
@not_logged_in_required
def register_user(request):
    form = UserRegistrationForm()
    company_id =  request.session.get('company_id')
    if company_id == None:
       if request.user.is_authenticated:
          return redirect('main:home') 
       else:
           return redirect('main:login') 
    else:
        company = company_table.objects.get(pk=company_id)
    
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        
        if company_id == "":
            messages.error(request, "You need company ID to register")
        else:
            if form.is_valid():
                user = form.save(commit=False)
                user.company_id = company
                user.set_password(form.cleaned_data.get('password'))
                user.save()
                messages.success(request, "Registration Successful")
            return redirect('main:login')

    context = {
        "form": form
    }
    return render(request, 'register.html', context)




@never_cache
@not_logged_in_required
def Login(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            us =  User.objects.filter(email=email)
            if us.exists():
                username = us.first().username
            else:
                username = email

            user = authenticate(
                username=username,
                password = form.cleaned_data.get('password')
            )
          
            if user:
                create_profile(request, user)
                login(request, user)
                return redirect('main:home')
                # del request.session['company_id']
                # del request.session['db_name']
            else:
                messages.warning(request, "Invalid Credentials !")

        else:
            pass
            # print(form.errors)

    context = {
        "form": form
    }
    return render(request, 'login.html', context)



def logout_user(request):
    logout(request)
    return redirect('main:login')

from django.db import connection
import subprocess
def MigrationPage(request):
    # db_name =  request.session.get('db_name')
    # company_id =  request.session.get('company_id')


    
    return render(request, "Migration.html")

def AddCompany(request):

    company = company_table.objects.all()
    if request.method == 'POST':
        db_name = 'afrikbook_'+generate_company_id()

        db = company_table.objects.filter(db_name=db_name)
        if db.exists():
            messages.success(request, "Database already exists")
        else:
            feedback = add_company(request, db_name)
            if feedback:
                return redirect('main:Migration')
            else:
               messages.success(request, "All fields must be filled in to submit")

    context = {
        'companys': company,
    }
    
    create_pages(request)
    create_country_currency(request)
    return render(request, "company_registration.html", context)

def VerifyEmail(request):
    email = request.GET.get('email')
    code = request.GET.get('code')
    title = "Email Verification"
    message ="Your verification code is <h1>"+code+"</h1>"

    send = send_email([email], title, message)

    return JsonResponse(send, safe=False)

def UpdateCompany(request, id):
    company = company_table.objects.get(id=id)
    companys = company_table.objects.all()
    
    if request.method == 'POST':    
        update_company(request, id)
        return redirect("Stockin:NewCompany")
        
    context = {
        "company": company,
        "companys": companys
    }   
    return render(request, "stockin/EditCompany.html", context)

def delete_Company(request, id):
    company = company_table.objects.get(id=id)
    company.delete()
    messages.error(request, "Company was deleted successfully")
    return redirect("/Stockin/NewCompany")



@login_required(login_url="/")
def home(request):
    db = request.user.company_id.db_name
    # print(db)
 
    profile = CreateProfile.objects.using(db).filter(CompanyName=request.user.company_id.company_name).first()
    cur = currency.objects.all()
    # if profile.ownerName == "":
    #     form = ProfileSetupForm(request.POST, request.FILES or None, instance=profile)
    # else:
    form = ProfileSetupForm(request.POST, request.FILES or None, instance=profile)
        # form = None
    
    today = date.today()

    customers = customer_table.objects.using(db).count()
    all_sales = customer_invoice.objects.using(db).values("invoiceID").distinct().count()
    all_stock = CreateStockIn.objects.using(db).count()
    all_stock = CreateStockIn.objects.using(db).count()
    expired_p = ExpiryDate.objects.using(db).filter(expiry_date__lte=today).count()
   
    total_ex = customer_invoice.objects.using(db).values("invoiceID").distinct().aggregate(expected_total=Sum("amount_expected"))['expected_total'] or 0
    total_pd = customer_invoice.objects.using(db).values("invoiceID").distinct().aggregate(paid_total=Sum('amount_paid'))['paid_total'] or 0
    
   
    total_amount = "0.00"
    
    if total_ex or total_pd :
       total_amount = total_ex + total_pd 
    
    # invoice = customer_invoice.objects.filter(invoice_date=today).values("invoiceID").distinct()
    

    today_ex = customer_invoice.objects.using(db).filter(invoice_date__date=today).values("invoiceID").distinct().aggregate(expected_total=Sum("amount_expected"))['expected_total'] or 0
    today_pd = customer_invoice.objects.using(db).filter(invoice_date__date=today).values("invoiceID").distinct().aggregate(paid_total=Sum('amount_paid'))['paid_total'] or 0

    today_sales = "0.00"
    if today_ex or today_pd:
       today_sales = today_ex + today_pd 
        
   
    
    

    sales = customer_invoice.objects.using(db).filter(invoice_date__date=today).values("invoiceID").distinct()
    distinct_sales = []

    for sale in sales:
        new_data =  customer_invoice.objects.using(db).filter(invoiceID=sale["invoiceID"]).values()
        amount_expected =  customer_invoice.objects.using(db).filter(invoiceID=sale["invoiceID"]).first().amount_expected
        amount_paid =  customer_invoice.objects.using(db).filter(invoiceID=sale["invoiceID"]).first().amount_paid
        if amount_expected:
           total = amount_expected 
        else:
            total = amount_paid

    

        def get_customer_or_vendor():
            invoice = customer_invoice.objects.using(db).filter(invoiceID=sale['invoiceID']).first()
            # print(invoice.cusID)
            if customer_table.objects.using(db).filter(customer_code=invoice.cusID):
                # return "Customer"
                return  customer_table.objects.using(db).get(customer_code=invoice.cusID).email or "No email"
            elif vendor_table.objects.using(db).filter(custID=invoice.cusID):
                return vendor_table.objects.using(db).get(custID=invoice.cusID).email or "No email"
            else:
                return "No email"

        accountType = get_customer_or_vendor()
        
        

        if new_data.exists():
            new_data = new_data.first()
            new_data['customer_email'] = accountType
            new_data['total'] = total
            distinct_sales.append(new_data)

    # for pagination
    distinct_sales = pagenation(request, distinct_sales, 1, 4)

    context = {
        'total_customers':customers,
        'all_sales':all_sales,
        'all_stock':all_stock,
        'sales':distinct_sales,
        'today_sales':today_sales,
        'expired_p':expired_p,
        'total_amount':total_amount,
        'profile': profile,
        'form': form,
        'country': cur
    }
    
    return render(request, 'home.html', context)


def GetItemDetails(request, item_id):
    db = request.user.company_id.db_name
    try:
        item = Item.objects.using(db).get(generated_code=item_id)
        # print(item)
        data = {
                    'desc': item.description,
                    'name': item.item_name,
                    'unit': item.selling_price,
                    'amount': item.purchase_price
                }
        return JsonResponse(data)
    except Item.DoesNotExist: 
        return JsonResponse({'error': 'Item not found'}, status=404)





@login_required(login_url="/")
def SalesPoint(request):
    db = request.user.company_id.db_name
    category = Category.objects.using(db).all()
    customer = customer_table.objects.using(db).all()
    vendor = vendor_table.objects.using(db).all()
    item = Item.objects.using(db).all()
    accounts = chart_of_account.objects.using(db).all()
    
     
    context = {
        'customers': customer,
        'vendor':vendor,
        'items': item,
        'accounts': accounts,
        'category': category
    }
    # print(category)
    return render(request, 'sales_point.html', context)



def fetch_items(request):
    db = request.user.company_id.db_name
    items = list(Item.objects.using(db).values())

    return JsonResponse({'items': items})



def fetch_items_by_keyword(request):
    db = request.user.company_id.db_name
    keyword = request.GET.get('keyword', '')
    items = Item.objects.using(db).filter(item_name__icontains=keyword).values()
    
    items = list(items)
    return JsonResponse(items, safe=False)



def fetch_all_items(request):
    db = request.user.company_id.db_name
    items = Item.objects.using(db).all()

    items_data = [{'id': item.id, 'item_name': item.item_name, 'generated_code': item.generated_code, 'selling_price': item.selling_price, 'image': str(item.image)} for item in items]

    return JsonResponse({'items': items_data})




def fetch_items_by_category(request, category_name):
    db = request.user.company_id.db_name
    category = Category.objects.using(db).get(category_name=category_name)
    items = Item.objects.using(db).filter(category=category)

  
    items_data = [{'id': item.id, 'item_name': item.item_name, 'generated_code': item.generated_code, 'selling_price': item.selling_price, 'image': str(item.image)} for item in items]

    return JsonResponse({'items': items_data})





def fetch_item_details(request):
    db = request.user.company_id.db_name
    item_code = request.GET.get('keyword', '')
    items = Item.objects.using(db).filter(generated_code__icontains=item_code).values().first()
    
    if items:
        return JsonResponse(items)
    



@require_POST
def add_to_cart(request, item_id):
    db = request.user.company_id.db_name
    item = Item.objects.using(db).get(generated_code=item_id)
    
    cart_items = {
        'quantity': 0, 
        'price': float(item.selling_price),
        'generated_code':str(item.generated_code),
    }
    request.session['cart'] = cart_items
    cart = request.session.get('cart', {})
 
    
    return JsonResponse({'message': 'Product added to cart successfully', 'cart':cart})






@login_required(login_url="/")
@urls_name(name="Users")
def NewUser(request):
    
    id = request.user.company_id_id
    db = request.user.company_id.db_name
    employees = employee.objects.using(db).all()

    user = User.objects.filter(company_id=id).all()
    # save_form = User.objects.using(db)
    form = NewUserForm()
    if request.method == "POST":
        em = request.POST.get('employee')
        username = request.POST.get('username')
        
        form = NewUserForm(request.POST)
        if em is None:
            messages.error(request, "Select employee")
        else:
            
            if form.is_valid():
                save_form = form.save(commit=False)
                save_form.username = username
                save_form.company_id_id = id
                save_form.set_password(form.cleaned_data.get('password'))
                save_form.save()
                messages.success(request, "Registration Successful")
                return redirect('main:NewUser')
            else:
                pass
                print(form.errors)
    context = {
        "form": form,
        "user": user,
        "employee": employees
    }
  
    return render(request, 'NewUser.html', context)



def GetUserDetails(request, id):
    try:
        user = User.objects.get(id=id)
        privilege = Privilege.objects.filter(user=id).values_list('name', flat=True)
        data = {
                'id': user.pk,
                'username': user.username,
                'email': user.email,
                'password': user.password,
                'outlet': user.outlet,
                'priviledge': list(privilege),
                # 'outlet': privilege.outlet,
            }
        return JsonResponse(data)
    except User.DoesNotExist: 
        return JsonResponse({'error': 'Vendor not found'}, status=404)
    



@csrf_exempt
@login_required(login_url='/')
@urls_name(name="Users")
def EditUser(request):
    db = request.user.company_id.db_name
    id = request.user.company_id_id

    show_user = User.objects.filter(company_id=id)
    view_page = Pages.objects.all()
    outlet = sales_outlet.objects.using(db).all()
    
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))

        user_id = data.get('id')
        username = data.get('username')
        privileges = data.get('privileges', [])

        # User instance
        user_instance = User.objects.get(id=user_id)

        Privilege.objects.filter(user=user_instance).update(is_active=False)

        for privilege_name in privileges:
            if not Privilege.objects.filter(user=user_instance, name=privilege_name).exists():
                # If the privilege doesn't exist, save it
                privilege = Privilege(user=user_instance, name=privilege_name, description='', is_active=True)
                privilege.save()
            else:
                privilege = Privilege.objects.get(user=user_instance, name=privilege_name)
                privilege.is_active = True
                privilege.save()
            

        return JsonResponse({'success': True, 'message': 'Privileges updated successfully'})
    
    return render(request, 'EditUser.html', {'show_user': show_user, 'view_page': view_page, 'outlet': outlet})
   



def remove_privilege(request, privilege_name):
    user_id = request.POST.get('id')
    user_instance = User.objects.get(id=user_id)
    try:
        user_privilege = Privilege.objects.get(user=user_instance, name=privilege_name)
        user_privilege.is_active = False
        user_privilege.save()
        return JsonResponse({'success': True, 'message': 'Privilege removed successfully'})
    except Privilege.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Privilege not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
    



@csrf_exempt
@login_required(login_url="/")
def update_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('id')
        username = request.POST.get('username')
        password = request.POST.get('password')
        c_password = request.POST.get('c-password')
        outlet = request.POST.get('outlet')  

        try:
            user = User.objects.get(id=user_id)
            user.username = username
            if password and c_password and password == c_password:
                user.set_password(password) 
            user.outlet = outlet
            user.save()

            return JsonResponse({'success': True, 'message': 'User updated successfully'})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})









def save_privileges(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))

        user_id = data.get('id')
        username = data.get('username')
        privileges = data.get('privileges', [])

        # Assuming you have a User instance
        user_instance = User.objects.get(id=user_id)

        # Save privileges in the Privilege model
        for privilege_name in privileges:
            privilege = Privilege(user=user_instance, name=privilege_name, description='', is_active=True)
            privilege.save()

        return JsonResponse({'success': True, 'message': 'Privileges updated successfully'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required(login_url="/")
def update_privilege_publish_status(request, privilege_id):

    privilege = Privilege.objects.get(pk=privilege_id)

    show_user = User.objects.all()

    if request.method == 'POST':
        is_published = request.POST.get('is_published')
        privilege.is_published = bool(is_published)
        privilege.save()
        return redirect('privilege_list')  # Redirect to a view displaying privileges

    return render(request, 'EditUser.html', {'privilege': privilege, 'show_user': show_user})



@csrf_exempt  
def update_privileges(request):
    if request.method == 'POST':
        data = request.POST.getlist('privilege[]')  # Assuming you have 'name="privilege"' for your checkboxes

        # Assuming each checkbox value is the privilege name
        privileges_to_update = Privilege.objects.filter(name__in=data)
        privileges_to_update.update(is_published=0)  # Update is_published based on your logic

        return JsonResponse({'success': True, 'message': 'Privileges updated successfully'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})


class DeletePrivilege(LoginRequiredMixin,UserPassesTestMixin, DeleteView):
    model = Privilege
    template_name ="delete.html"
    success_url ="/list_privileges"

    def test_func(self):
        ##HOW TO GET THE QUERYSET INSTANCE
        ##self.get_object()
        
        ##HOW TO GET THE LOGGED IN USER
        #self.request.user

        return self.get_object().creator == self.request.user
   

class UpdatePrivilege(LoginRequiredMixin,UpdateView):
    model = Privilege
    template_name ="update.html"
    fields = ['name', 'description']
    success_url ="/list_privileges"   


@login_required
def list_Privileges(request):
    Privileges = Privilege.objects.all()
    # Privileges = Privilege.objects.filter(creator=request.user).order_by("-id")
    # print(Privileges)
    return render(request, "list_privileges.html",{"Privileges":Privileges})


@login_required
def create_Privilege(request):
    # form = TestForm()
    form = PrivilegeForm()


    if request.method == "POST":
        
        form = PrivilegeForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Privilege was created successfully")

            
            return redirect("/list_privileges")


    return render(request, "create_privilege.html",{"form":form})


@login_required(login_url="/")
def add_pages(request):
    pages = ['Chart of account', 'Purchase Invoices', 'Purchase Invoices', 'Purchase Order',
              ' Returns Outwards', 'Vendor', 'Sales Invoices', 'Sales Quotes', 'Sales Order', 
              'Returns Inwards', 'Customer', 'Employee', 'Payroll', 'Salary Approval', 'Item Receipt', 
              'Item Issue', 'Transfer Stock', 'Stock Adjustment', 'Item', 'Journal Entries', 'Loan Manager',
              'Sales Report', 'Stock In Report', 'Purchase Report', 'Purchase Adjustment', 'Stock Adjustment Outlet',
              'Payroll Report', 'Receivables', 'Payables', 'Aged Receivables', 'Aged Payable', 'Accounts', 
              'General Ledger', 'Balance Sheet', 'Balance Sheet', 'Price Management', 'Users', 'Add Warehouse', 
              'Server Setup', 'Profile Setup', 'Sales Unit', 'Inter Account Transfer', 'Expired Items', 'Customer Incentives'
              'Warehouse to Outlet', 'Outlet to Warehouse', 'Stock Adjustment', 'Verify Transfer', 'Add New Journal',
              'Receive Payment', 'View Journal Entries', 'Profit / Loss', 'Other Series', 'Customer Ledger', 'Sales Ledger',
              'Purchase Ledger ', 'Vendor Ledger', 'Add New Item', 'Item Category', 'Stock Level', 'Dashboard', 'Profile',
              'Purchase Price (Optional)', 'Selling Price (Retail)', 'Selling Price (Wholesale)', 'Change Price',
              '2.5% Sales Discount', '5% Sales Discount', '7.5% Sales Discount', '10% Sales Discount', '12.5% Sales Discount',
              'Change Sales Price'
            ]
    db = request.user.company_id.db_name
    form = PagesForm()
    if request.method == "POST":
        
        form = PagesForm(request.POST)

        if form.is_valid():
            form_i = form = form.save(commit=False)
            form_i.save(using=db)
            messages.success(request, "Page was created successfully")
            

            
            return redirect("/add_page")


    return render(request, "create_page.html",{"form":form})



# Sidebar page
# @user_page_permission(name='AddVendor')
def AddVendor(request):
   
    return render(request, 'pages/AddVendor.html')


@login_required(login_url="/")
def Grant_Permission(request, username=None):
    db = request.user.company_id.db_name
    user = get_object_or_404(User, username=username)
    user_form = UserSettingsForm(request.POST or None,request=request, instance=user)
    permissions = [(p.id, p.name) for p in Permission.objects.using(db).filter(user=user)]
    data = {
        'acct_holder' : user,
        'form' : user_form,
        'from': request.GET.get('from', None),
        'permissions' : permissions,
    }

    if request.POST:
        if user_form.is_valid():
            user = user_form.save()
            next = request.GET.get('next', None)
            return redirect(next)
    return render(request, "grant_permission.html", data)

































@login_required(login_url="/")
def privilege_settings(request):
    privileges = Privilege.objects.all()

    if request.method == 'POST':
        data = request.POST
        privilege_name = data.get('warehouse_to_outlet')

        try:
            privilege = Privilege.objects.get(name=privilege_name)
        except Privilege.DoesNotExist:
            privilege = Privilege(name=privilege_name)
        
        privilege.is_published = data.get('is_published', False)
        privilege.save(using=db)

        updated_privileges = {privilege.name: privilege.is_published for privilege in Privilege.objects.all()}

        return JsonResponse({'success': True, 'message': 'Privilege updated successfully', 'privileges': updated_privileges})

    return render(request, 'pri.html', {'privileges': privileges})



def insert_items(request):
    db = request.user.company_id.db_name
    message_displayed = False  # Initialize the message_displayed variable
    executed = False 

    if request.method == 'POST':
        data = json.loads(request.body)
        items = data.get('items', [])
        total = decimal.Decimal(data.get('total'))
        payment_method = data.get('payment_method')
        acc = data.get('account')
        accountType = data.get('accountType')
        cus_id = data.get('cus_id')
        ven_id = data.get('ven_id')


        invoiceID = generate_invoice_id()
        order_id = generate_order_id()
        invoice_date = date.today()
        due_date = date.today()
        invoice_state = "Supplied"
        # Generate a new transaction ID
        transaction_id = uuid.uuid4()

        # Generate refrence number
        ref_no = "REF"+generate_order_id()

        Gdescription = "Sales Point"

        if payment_method:
            amount_paid = total
            amount_expected = 0.00

        if accountType == "Customer":
            if cus_id  == "Casual Customer":
                customer = customer_table.objects.using(db).get(name=cus_id)
                customer_name = customer.name
                cusID = customer.customer_code
            else:
                customer = customer_table.objects.using(db).get(customer_code=cus_id)
                customer_name = customer.name
                cusID = customer.customer_code
        elif accountType == "Vendor":
            customer = vendor_table.objects.using(db).get(custID=ven_id)
            customer_name = customer.name
            cusID = customer.custID
       
        account = chart_of_account.objects.using(db).get(account_id =acc)
        total_purchaseP = 0.00

        outlet = User.objects.using(db).get(id = request.user.id).outlet or None
        
        if outlet != None:
            # Insert items into the database
            for item in items:
                # Perform database insertion logic here
                itemcode  = item[0]
                item_name = item[2]
                price     = item[3]
                quantities       = item[4]
                Item_ =  Item.objects.using(db).filter(generated_code=itemcode).first()

                amount = decimal.Decimal(price) * int(quantities)

                # int_purchaseP = [int(num) if num.isdigit() else 0 for num in Item.purchase_price ]

                # total_purchaseP = Item.objects.filter(generated_code=item[0]).aaggregate(total =Sum('purchase_price'))

                # print(itemcode,  Item.purchase_price)
                # pass
                form_data = {
                    'cusID': cusID,
                    'customer_name':customer_name,
                    'invoice_date':invoice_date,
                    'due_date': due_date,
                    'invoiceID':invoiceID ,
                    'order_ID':order_id ,
                    'Gdescription': Gdescription,
                    'item_name': item_name,
                    'itemcode': itemcode,
                    'item_description': Item_.description,
                    'qty': quantities,
                    'unit_p':price,
                    'discount': 0.00,
                    'amount': amount,
                    'amount_paid': amount_paid,
                    'amount_expected': amount_expected,

                    "cancellation_status":0,
                    "status":1,
                    "Transfer":0,
                    "POS":0,
                    "Cash":0,
                    "Customer_account":0,
                    "Cheque":0,
                    "invoice_state":"Supplied",
                    "purchaseP":Item_.purchase_price,
                    "total_purchaseP":total_purchaseP
                }
                cus_form = CustomerSalesForm(form_data)

            # if credit_sales == None:
                if accountType == "Customer": 
                    receivable_form = ReceivableForm({"date":invoice_date,	"description":Gdescription,"type": "Debit",	"amount": amount_paid, "payment_method": payment_method,"invoice_status": "Unused"})

                    if cus_id == "Casual Customer":
                                        
                        casual_account = chart_of_account.objects.using(db).get(account_id =acc)
                        cus = customer_table.objects.using(db).get(name=cus_id)

                        if cus_form.is_valid() and receivable_form.is_valid():
                                form = cus_form.save(commit=False)
                                form.Userlogin = request.user.username
                                form.save(using=db)
            
                                #Reduce stock quantity
                                if invoice_state == "Supplied":
                                    outlet= request.user.outlet
                                    ReduceOutletStockinItemQuantity(db, outlet, itemcode, quantities)
                                    
                                if not message_displayed:
                                    if invoice_state == "Supplied":
                                        # make changes in the customer balance and invoice
                                        # cus.Balance = cus.Balance - decimal.Decimal(amount_paid)
                                        cus.invoice = cus.invoice + 1
                                        cus.save()

                                        # make changes in the chat of account
                                        casual_account.actual_balance += total
                                        casual_account.save()

                                        #get customer last recievable balance 
                                        if receivable.objects.using(db).filter(customer_id=cus.customer_code).exists():
                                            initial_bal = receivable.objects.using(db).filter(customer_id=cus.customer_code).last().balance
                                        else: 
                                            initial_bal = decimal.Decimal(0.00)

                                        # insert into recievable
                                        r_form = receivable_form.save(commit=False)
                                        r_form.customer_id = cus.customer_code
                                        r_form.customer_name = cus.name
                                        r_form.initial_amount = initial_bal
                                        r_form.balance = decimal.Decimal(initial_bal) + total
                                        r_form.account_posted = casual_account.account_id # default account
                                        r_form.transaction_id = transaction_id
                                        r_form.Userlogin = request.user.username
                                        r_form.save(using=db)

                                        messages.success(request, "Invoice supplied")
                                        message_displayed = True  # Update the message_displayed variable
                                    else:
                                        cus.invoice = cus.invoice + 1
                                        cus.save()
                                        messages.success(request, "Invoice Pending")
                                        message_displayed = True  # Update the message_displayed variable
                                    #create account log
                                    acc_log = account_log(
                                        transaction_source  = "Sales",
                                        amount              = total,
                                        date                = invoice_date,
                                        account             = casual_account.account_id,
                                        account_type        = casual_account.account_type,
                                        Userlogin = request.user.username
                                    )
                                    acc_log.save(using=db)
                                    # messages.success(request, "New Sales Invoice was added successfully")
                                    message_displayed = True  # Update the message_displayed variable
                                    # return JsonResponse({'message': 'New Sales Invoice was added successfully'}, status=200)
                        else:
                                pass
                                # print("Customer form error", cus_form.errors)
                                # print("Receivable form error", receivable_form.errors)
                    else:
                        if not executed:
                            # check if invoice number exists
                            if customer_invoice.objects.using(db).filter(invoiceID=invoiceID).exists():
                                if not message_displayed:
                                    messages.error(request, "Invoice Number already exist")
                                    message_displayed = True
                            # check if customer is selected
                            if not cusID or int(cusID) < 1:
                                if not message_displayed:
                                    messages.error(request, "Select Customer")
                                    message_displayed = True
                            # fetch selected customer
                            cus = customer_table.objects.using(db).get(customer_code=cusID)
                            # check if customer balance is sufficient
                            # if total > cus.Balance:
                            #     if not message_displayed:
                            #         messages.error(request, "Insufficient fund")
                            #         message_displayed = True
                            executed = True
                        if executed:
                            if cus_form.is_valid() and receivable_form.is_valid():
                                form = cus_form.save(commit=False)
                                form.Userlogin = request.user.username
                                form.save(using=db)
            
                                #Reduce stock quantity
                                if invoice_state == "Supplied":
                                    outlet= request.user.outlet
                                    ReduceOutletStockinItemQuantity(db, outlet, itemcode, quantities)

                                if not message_displayed:
                                    if invoice_state == "Supplied":
                                        # make changes in the customer balance and invoice
                                        # cus.Balance = cus.Balance - decimal.Decimal(amount_paid)
                                        cus.invoice = cus.invoice + 1
                                        cus.save()

                                        # make changes in the chat of account
                                        account.actual_balance += total
                                        account.save()

                                        #get customer last recievable balance 
                                        if receivable.objects.using(db).filter(customer_id=cusID).exists():
                                            initial_bal = receivable.objects.using(db).filter(customer_id=cusID).last().balance
                                        else: 
                                            initial_bal = decimal.Decimal(0.00)

                                        # insert into recievable
                                        r_form = receivable_form.save(commit=False)
                                        r_form.customer_id = cus.customer_code
                                        r_form.customer_name = cus.name
                                        r_form.initial_amount = initial_bal
                                        r_form.balance = decimal.Decimal(initial_bal) + total
                                        r_form.account_posted = account.account_id # default account
                                        r_form.transaction_id = transaction_id
                                        r_form.Userlogin = request.user.username
                                        r_form.save(using=db)

                                        messages.success(request, "Invoice supplied")
                                        message_displayed = True  # Update the message_displayed variable
                                    else:
                                        cus.invoice = cus.invoice + 1
                                        cus.save()
                                        messages.success(request, "Invoice Pending")
                                        message_displayed = True  # Update the message_displayed variable
                                    #create account log
                                    acc_log = account_log(
                                        transaction_source  = "Sales",
                                        amount              = total,
                                        date                = invoice_date,
                                        account             = account.account_id,
                                        account_type        = account.account_type,
                                        Userlogin = request.user.username
                                    )
                                    acc_log.save(using=db)
                                    message_displayed = True  # Update the message_displayed variable
                            else:
                                pass
                                # print("Customer form error", cus_form.errors)
                                # print("Receivable form error", receivable_form.errors)
                if accountType == "Vendor":
                    payable_form = PayableForm({"date":invoice_date,	"description":Gdescription,"type": "Credit",	"amount": amount_paid, "payment_method": "Transfer","account_posted":account.account_id,"invoice_status": "Unused"})
                    if not executed:
                        # check if invoice number exists
                        if Vendor_invoice.objects.using(db).filter(invoiceID=invoiceID).exists():
                            if not message_displayed:
                                messages.error(request, "Invoice Number already exist")
                                message_displayed = True
                        # check if customer is selected
                        if not ven_id or int(ven_id) < 1:
                            if not message_displayed:
                                messages.error(request, "Select Vendor")
                                message_displayed = True
                        # fetch selected vendor
                        ven = vendor_table.objects.uing(db).get(custID=ven_id)
                        
                        executed = True
                    if executed:
                        if cus_form.is_valid() and payable_form.is_valid():
                            form = cus_form.save(commit=False)
                            form.Userlogin = request.user.username
                            form.save(using=db)

                            #Reduce stock quantity
                            if invoice_state == "Suplied":
                                outlet= request.user.outlet
                                ReduceOutletStockinItemQuantity(db, outlet, itemcode, quantities)

                            if not message_displayed:
                                if invoice_state == "Suplied":
                                    # make changes in the customer balance and invoice
                                    # cus.Balance = cus.Balance - decimal.Decimal(amount_paid)
                                    ven.invoice = ven.invoice + 1
                                    ven.save()

                                    # make changes in the chat of account
                                    account.actual_balance += total
                                    account.save()

                                    if payable.objects.using(db).filter(customer_id=cusID).exists():
                                        initial_bal = payable.objects.using(db).filter(customer_id=cusID).last().balance
                                    else: 
                                        initial_bal = decimal.Decimal(0.00)

                                    # insert into payable
                                    
                                    
                                    p_form = payable_form.save(commit=False)
                                    p_form.customer_id = ven.custID
                                    p_form.customer_name = ven.name
                                    p_form.initial_amount = initial_bal
                                    p_form.balance = decimal.Decimal(initial_bal) + total
                                    # p_form.account_posted = "default account" # default account
                                    p_form.transaction_id = transaction_id
                                    p_form.Userlogin = request.user.username
                                    p_form.save(using=db)

                                    
                                    messages.success(request, "Invoice supplied")
                                    message_displayed = True  # Update the message_displayed variable
                                else:
                                    ven.invoices = ven.invoices + 1
                                    ven.save()
                                    messages.success(request, "Invoice Pending")
                                    message_displayed = True  # Update the message_displayed variable
                                #create account log
                                acc_log = account_log(
                                    transaction_source  = "Sales",
                                    amount              = total,
                                    date                = invoice_date,
                                    account             = account.account_id,
                                    account_type        = account.account_type,
                                    Userlogin = request.user.username
                                )
                                acc_log.save(using=db)
                                # messages.success(request, "New Sales Invoice was added successfully")
                                message_displayed = True  # Update the message_displayed variable
                                # return JsonResponse({'message': 'New Sales Invoice was added successfully'}, status=200)
                        else:
                            pass
                            # print("Customer form error", cus_form.errors)
                            # print("Receivable form error", payable_form.errors)
                
            return JsonResponse(data ={'type':'success','message': 'New Sales Invoice was added successfully'}, status=200)
        else:
            return JsonResponse(data ={'type':'error','message': 'Assign outlet to logged in user'}, status=200)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


from django.core.mail import send_mail,  EmailMessage
from django.conf import settings
from io import BytesIO

def send_email(email, title, message):
   
    result = send_mail(
        title, 
        message, 
        settings.EMAIL_HOST_USER, 
        email, 
        fail_silently=False,
        html_message=message
    )


    if result == len(email):
        return True
    else:
        return False

def send_email_with_pdf(request):

    html_content = request.GET.get('html_content')

    if 'pdf_file' not in request.FILES:
        return JsonResponse({'success': False, 'error': 'No file uploaded'})

    pdf_file = request.FILES['pdf_file']
    receipient_email = request.POST['email']
    
    
    if not pdf_file or not receipient_email:
        return JsonResponse({'error': 'Invalid data'}, status=400)
    
    # pdf_file = generate_pdf_from_text(html_content)

    # receipient_email = 'isdoremartins23@gmail.com'
    subject = "From Afrikbook"
    message = "welcome to Afrikbook account system"
    html_msg = '<h1>THANK YOU !!!</h1>'

    email = EmailMessage(
        subject, 
        message, 
        settings.EMAIL_HOST_USER, 
        [receipient_email], 
    )
    pdf = 'media/profiles/image_4.png'
    email.attach('document.pdf', pdf_file.read(), 'application/pdf')
    email.send(fail_silently=False)

    return JsonResponse({'success': True})


# def generate_pdf_from_text(text):
#     pdf_file = BytesIO()
#     c = canvas.Canvas(pdf_file, pagesize=letter)
#     c.drawString(100, 750, text)
#     c.showPage()
#     c.save()
#     pdf_file.seek(0)
#     return pdf_file
