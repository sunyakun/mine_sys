from django.urls import path
from . import views

app_name = 'mine'
urlpatterns = [
    path('', views.training_view, name='training')
]