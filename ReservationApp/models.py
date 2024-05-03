from django.db import models

class DietaryRestriction(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Endorsement(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Diner(models.Model):
    name = models.CharField(max_length=100)
    dietary_restrictions = models.ManyToManyField(DietaryRestriction)

    def __str__(self):
        return self.name

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    endorsements = models.ManyToManyField(Endorsement)

    def __str__(self):
        return self.name

class Table(models.Model):
    capacity = models.PositiveIntegerField()
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables')  


    def __str__(self):
        return f"Table {self.id} at {self.restaurant.name}"

class Reservation(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    diners = models.ManyToManyField(Diner)
    time = models.DateTimeField()

    def __str__(self):
        diner_names = ', '.join(diner.name for diner in self.diners.all())
        return f"Reservation ID: {self.id} for {diner_names} at {self.table.restaurant.name} - Table {self.table.id}"