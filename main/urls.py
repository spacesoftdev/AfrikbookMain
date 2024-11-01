from django.urls import path
# from .views import FilterItemsByCategoryView
from main import views

app_name="main"

urlpatterns = [
    path('register', views.register_user, name='register'),

    path('', views.Login, name='login'),

    path('Logout/', views.logout_user, name='logout'),

    path('Migration', views.MigrationPage, name='Migration'),

    # Company
    path('NewCompany', views.AddCompany, name='NewCompany'),
    path('StockinUpdate/<int:id>/', views.UpdateCompany, name='updateCompany'),
    path('StockinDelete/<int:id>/', views.delete_Company, name='delete-company'),

    path('home', views.home, name='home'),

    path('SalesPoint', views.SalesPoint, name='SalesPoint'),
    path('fetch-items/', views.fetch_items, name='fetch_items'),
    path('fetch-all-items/', views.fetch_all_items, name='fetch_all_items'),
    path('fetch-items-by-keyword/', views.fetch_items_by_keyword, name='fetch_items_by_keyword'),
     path('fetch_item_details/', views.fetch_item_details, name='fetch_item_details'),
   
    path('fetch-items-by-category/<str:category_name>/', views.fetch_items_by_category, name='fetch_items_by_category'),



    # add to cart and javascript dynamic view 
    path('add-to-cart/<str:item_id>/', views.add_to_cart, name='add_to_cart'),

    path('New-User', views.NewUser, name='NewUser'),
    path('Edit-User', views.EditUser, name='EditUser'),
    path('remove-privilege/<str:privilege_name>/', views.remove_privilege, name='remove_privilege'),
    path('get_user/<int:id>/', views.GetUserDetails, name='item-details'), #ajax
    path('update-user/', views.update_user, name='update_user'), #ajax
    path('Add-Vendor', views.AddVendor, name='AddVendor'),

    
    path("create_privilege", views.create_Privilege, name="create_privilege"),
    path("delete_privilege/<int:pk>", views.DeletePrivilege.as_view(), name="delete_privilege"),
    path("update/<int:pk>", views.UpdatePrivilege.as_view(), name="update_privilege"),
    path("list_privileges", views.list_Privileges, name="list_privileges"),

    path('update-privilege/<int:privilege_id>/', views.update_privilege_publish_status, name='update_privilege_publish'),


    path('update_privileges/', views.update_privileges, name='update_privileges'),

     path('privilege_settings/', views.privilege_settings, name='privilege_settings'),


    path("grant_permission", views.Grant_Permission, name="grant_permission"),

    path("save_privileges/", views.save_privileges, name="save_privileges"),
    path("add_page", views.add_pages, name="add_page"),


    path('insert_items', views.insert_items, name='insert_items'),
    path('send_email_with_pdf', views.send_email_with_pdf, name='send_email_with_pdf'),
    
    path('VerifyEmail', views.VerifyEmail, name='VerifyEmail'),
]  
