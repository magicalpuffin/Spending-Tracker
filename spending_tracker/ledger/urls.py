from django.urls import path

from . import views

app_name = 'ledger'

urlpatterns = [
    path('', views.IndexView.as_view(), name= 'index'),
    path('transaction/', views.TransactionIndexView.as_view(), name= 'transaction-index'),
    path('transaction/create/', views.transaction_create, name= 'transaction-create'),
    path('transaction/delete/<int:pk>', views.transaction_delete, name= 'transaction-delete'),
    path('transaction/table-load/', views.load_transaction_table, name= 'transaction-table-load'),
    path('transaction/upload/', views.transaction_upload, name= 'transaction-upload'),
    path('type/', views.TypeIndexView.as_view(), name= 'type-index'),
    path('type/create/', views.type_create, name= 'type-create'),
    path('type/delete/<int:pk>', views.type_delete, name= 'type-delete'),
    path('type/table-load/', views.load_type_table, name= 'type-table-load'),
]