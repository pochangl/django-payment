from django.contrib import admin
from .models import Order, PaymentErrorLog


class ReadOnlyAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields

        if self.declared_fieldsets:
            return flatten_fieldsets(self.declared_fieldsets)
        else:
            return list(set(
                [field.name for field in self.opts.local_fields] +
                [field.name for field in self.opts.local_many_to_many]
            ))

class OrderAdmin(ReadOnlyAdmin):
    list_display = ('id', 'order_no', 'owner', 'product_class', 'title', 'payment_amount', 'payment_received', 'handled')


class ErrorAdmin(ReadOnlyAdmin):
    list_display = ('id', 'path', 'resolved')
    list_filter = ('resolved', )

admin.site.register(Order, OrderAdmin)
admin.site.register(PaymentErrorLog, ErrorAdmin)

