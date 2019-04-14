from django.db import models


class ProductModel(models.Model):
    name = models.CharField(max_length=16)
    description = models.CharField(max_length=16)
    price = models.PositiveIntegerField()

    buyers = models.ManyToManyField('auth.User')
