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
    path('type/create/', views.TypeCreateView.as_view(), name= 'type-create'),
    path('type/delete/<int:pk>', views.TypeDeleteView.as_view(), name= 'type-delete'),
    path('type/update/<int:pk>', views.TypeUpdateView.as_view(), name= 'type-update'),
    path('type/load-table/', views.LoadTypeTableView.as_view(), name= 'type-load-table'),
]

urlpatterns += transaction_urlpatterns
urlpatterns += type_urlpatterns