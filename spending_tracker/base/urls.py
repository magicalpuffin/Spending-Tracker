from django.urls import path

from . import views

app_name = 'base'

urlpatterns = [
    path('', views.IndexView.as_view(), name= 'index'),
    path('load-messages', views.load_messages, name= 'load-messages'),
]