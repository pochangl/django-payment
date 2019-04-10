import inspect
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from .models import Order
from .exceptions import DuplicatePayment


def update_order(details):
    '''
        mark order received
    '''
    try:
        order = Order.objects.get(order_no=details["order_no"])
    except Order.DoesNotExist:
        raise ValidationError("Order Does Not Exist. order_no: %s" %
                              details["order_no"])

    # duplicate entry
    if order.payment_received:
        raise DuplicatePayment("duplicate payment: pay "
                               "has already been proceed")
    if order.payment_amount != details["payment_amount"]:
        raise ValidationError(
            "Payment amount does not meet our record, %s: %s" %
            (__name__, inspect.currentframe().f_back.f_lineno))

    order.additional_fee = details["additional_fee"]
    order.payment_received = now()
    order.save()
    details["order"] = order
