from django.db import models

class Table(models.Model):
    table_number = models.IntegerField(unique=True)
    num_seats = models.IntegerField()
    

class Reservation(models.Model):
    start_time = models.DateTimeField(db_index=True) 
    end_time = models.DateTimeField()
    table = models.ForeignKey('TableMangement.Table', on_delete=models.PROTECT, null=True)