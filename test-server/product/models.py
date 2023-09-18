from django.db import models


class Book(models.Model):
    book_title = models.CharField(max_length=16)
    book_description = models.CharField(max_length=16)
    book_price = models.PositiveIntegerField()

    buyers = models.ManyToManyField('auth.User', through='product.BookOwner')

    is_active = models.BooleanField(default=False)
    count = models.IntegerField(default=0)  ## count how many times applied


class BookOwner(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
