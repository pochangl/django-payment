from django.contrib import admin
from django.contrib.admin.utils import flatten_fieldsets
from .models import Order, PaymentErrorLog


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_no', 'owner', 'product_class', 'title', 'payment_amount', 'payment_received', 'handled', 'time_created')
    readonly_fields = list_display


class ErrorAdmin(admin.ModelAdmin):
    list_display = ('id', 'path', 'resolved')
    list_filter = ('resolved', )
    readonly_fields = list_display

admin.site.register(Order, OrderAdmin)
admin.site.register(PaymentErrorLog, ErrorAdmin)
