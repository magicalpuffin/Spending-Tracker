from django.db import models

import random

def generate_random_id():
    random_num = random.randint(100000000, 999999999)

    return random_num

# Create your models here.

class Type(models.Model):
    name= models.CharField(max_length=256)

    def __str__(self) -> str:
        return self.name

class Transaction(models.Model):
    ref_num= models.CharField(max_length=256, default= generate_random_id, unique= True)
    source= models.CharField(max_length=256)
    trans_date= models.DateTimeField()
    name= models.CharField(max_length=256)
    amount= models.DecimalField(max_digits=16, decimal_places=2)
    type= models.ManyToManyField(Type, through= 'TransactionType')

    def __str__(self) -> str:
        return self.name
    
class TransactionType(models.Model):
    transaction= models.ForeignKey(Transaction, on_delete= models.CASCADE)
    type= models.ForeignKey(Type, on_delete= models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields= ['transaction', 'type'], name= 'unique transaction type')
        ]