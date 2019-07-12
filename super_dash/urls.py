from django.urls import path
from . import views

app_name = 'super_dash'
urlpatterns = [
    path('', views.index_view,
         name='index'),
    path('message/', views.message_view,
         name='message'),
    path('login/', views.login_view,
         name='login'),
    path('register/', views.register_view,
         name='register'),
    path('forgot-password/', views.forgot_password_view,
         name='forgot-password'),
    path('logout/', views.logout_view,
         name='logout'),
    path('profile/', views.profile_view,
         name='profile'),
    path('update_profile/', views.update_profile_view,
         name='update_profile'),
    path('get_task_status/', views.get_task_status_view,
         name='get_task_status'),
    path('upload_dataset/', views.upload_dataset_view,
         name='upload_dataset'),
    path('show_reports/', views.show_reports_view,
         name='show_reports'),
    path('get_dataset/', views.get_dataset_view,
         name='get_dataset'),
    path('settings/', views.settings_view,
         name='settings'),
    path('update_settings/', views.update_settings_view,
         name='update_settings'),
    path('get_dataset_overview/', views.get_dataset_overview,
         name='get_dataset_overview'),
    path('delete_dataset/', views.delete_dataset_view,
         name='delete_dataset'),
    path('echart/', views.echart_view,
         name='echart'),
    path('get_dataset_index/', views.get_dataset_index_view,
         name='get_dataset_index'),
    path('get_dataset_config/', views.get_dataset_config_view,
         name='get_dataset_config'),
    path('predict/', views.predict_view,
         name='predict')
]

handler404 = 'super_dash.views.response_not_found_handler'
