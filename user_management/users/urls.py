from django.urls import path
from.import views

urlpatterns = [
    path('',views.register_page,name='register_page'),
    path('login_page',views.login_page,name='login_page'),
    path('home_page',views.home_page,name='home_page'),
    path('logout_page',views.log_out,name='log_out'),
    
    path('admin_login',views.admin_login,name='admin_login'),
    path('admin_page',views.admin_page,name='admin_page'),
    path('admin_create_user',views.admin_create_user,name='admin_create_user'),
    path('admin_edit_user/<int:user_id>/',views.admin_edit_user,name='admin_edit_user'),
    path('admin_delete_user/<int:user_id>/',views.admin_delete_user,name='admin_delete_user'),
    path('admin_logout',views.admin_logout,name='admin_logout'),




]
