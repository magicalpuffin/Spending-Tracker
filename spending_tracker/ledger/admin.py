from django.contrib import admin
from ledger.models import Transaction, Type

# Register your models here.
admin.site.register(Transaction)
admin.site.register(Type)