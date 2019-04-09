import importlib
from django.conf import settings
from .exceptions import DuplicatePayment

def load_pipe(pipe_variable):
    pipes = []
    for pipe in pipe_variable:
        module_name, obj_name = pipe.rsplit('.', 1)
        m = importlib.import_module(module_name)
        obj = getattr(m, obj_name)
        pipes.append(obj)
    return pipes

default_pipes = [
    'payment.update_order'
]

payment_pipes = settings.SUCCESS_PAYMENT_PIPE if hasattr(settings, 'SUCCESS_PAYMENT_PIPE') else default_pipes

payment_pipes = load_pipe(settings.SUCCESS_PAYMENT_PIPE)


def receive_payment(details):
    try:
        for pipe in payment_pipes:
            details = pipe(details)
    except DuplicatePayment:
        return
