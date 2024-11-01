from django.shortcuts import redirect
from main.models import Privilege
from django.contrib import messages
def urls_name(name):
    # print(name)

    def user_page_permission(view_function):
        def wrapper(request, *args, **kwargs):
            db = request.user.company_id.db_name
            if request.user.is_authenticated:
                Privileges = Privilege.objects.filter(name=name,is_active = 1, user_id=request.user.id)
                if Privileges.exists():
                    return view_function(request, *args, **kwargs)
                else:
                    messages.error(request, "You dont have the privilage to access "+name+" page")
                    return redirect('main:home')
                    
            else:
                return view_function(request, *args, **kwargs)
                
        return wrapper
    return user_page_permission