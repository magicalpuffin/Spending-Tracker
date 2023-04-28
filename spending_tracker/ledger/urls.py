from django.urls import path

from . import views

app_name = 'ledger'

urlpatterns = [
    path('', views.IndexView.as_view(), name= 'index'),
]

transaction_urlpatterns = [
    path('transaction/', views.TransactionIndexView.as_view(), name= 'transaction-index'),
    path('transaction/create/', views.TransactionCreateView.as_view(), name= 'transaction-create'),
    path('transaction/delete/<int:pk>', views.TransactionDeleteView.as_view(), name= 'transaction-delete'),
    path('transaction/update/<int:pk>', views.TransactionUpdateView.as_view(), name= 'transaction-update'),
    path('transaction/load-table/', views.LoadTransactionTableView.as_view(), name= 'transaction-load-table'),
    path('transaction/upload/', views.TransactionUploadView.as_view(), name= 'transaction-upload'),
]

type_urlpatterns = [
    path('type/', views.TypeIndexView.as_view(), name= 'type-index'),
    path('type/create/', views.type_create, name= 'type-create'),
    path('type/delete/<int:pk>', views.type_delete, name= 'type-delete'),
    path('type/table-load/', views.load_type_table, name= 'type-table-load'),
]

urlpatterns += transaction_urlpatterns
urlpatterns += type_urlpatterns