import importlib
import inspect
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from .models import Order
from .exceptions import DuplicatePayment
from .utils import products
from .strategies import backends


# pip loading
default_pipes = [
    'payment.pipes.update_order',
    'payment.pipes.apply_order',
]

def load_pipe(pipe_variable):
    pipes = []
    for pipe in pipe_variable:
        module_name, obj_name = pipe.rsplit('.', 1)
        m = importlib.import_module(module_name)
        obj = getattr(m, obj_name)
        pipes.append(obj)
    return pipes

def receive_payment(details):
    kwargs = {
        'details': details
    }
    try:
        for pipe in payment_pipes:
            result = pipe(**kwargs)
            if result:
                kwargs.update(result)
    except DuplicatePayment:
        return


# actual pipe
def update_order(details, **kwargs):
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
        raise DuplicatePayment("duplicate payment: payment "
                               "has already been processed")
    if order.payment_amount != details["payment_amount"]:
        raise ValidationError(
            "Payment amount does not meet our record, %s: %s" %
            (__name__, inspect.currentframe().f_back.f_lineno))

    order.additional_fee = details["additional_fee"]
    order.payment_received = now()
    order.save()
    return {
        'order': order
    }

def apply_order(order, **kwargs):
    if order.handled:
        return
    Product = products[order.product_class]
    backend = backends[order.backend]
    product = Product(item=order.content_object, backend=backend)
    product.apply(order.owner)
    order.handled = True
    order.save()

payment_pipes = settings.SUCCESS_PAYMENT_PIPE if hasattr(settings, 'SUCCESS_PAYMENT_PIPE') else default_pipes
payment_pipes = load_pipe(payment_pipes)
