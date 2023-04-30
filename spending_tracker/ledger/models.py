from django.db import models
from django.contrib.auth.models import User

import random
from datetime import date

def generate_random_id():
    '''
    Generates a random 9 digit int
    '''
    random_num = random.randint(100000000, 999999999)

    return random_num

# Create your models here.

class Type(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name= models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(fields= ['creator', 'name'], name= 'unique type creator name ')
        ]

# One to many relationship between Type and Transaction
class Transaction(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    ref_num= models.CharField(max_length=256, default= generate_random_id)
    source= models.CharField(max_length=256)
    trans_date= models.DateField(default= date.today)
    name= models.CharField(max_length=256)
    amount= models.DecimalField(max_digits=16, decimal_places=2)
    
    type= models.ForeignKey(Type, on_delete= models.SET_NULL, blank= True, null= True)

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields= ['creator', 'ref_num'], name= 'unique transaction creator ref_num ')
        ]

# Was going to create a manytomany field, this idea might be reused for a tags
# class TransactionType(models.Model):
#     transaction= models.ForeignKey(Transaction, on_delete= models.CASCADE)
#     type= models.ForeignKey(Type, on_delete= models.CASCADE)

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(fields= ['transaction', 'type'], name= 'unique transaction type')
#         ]