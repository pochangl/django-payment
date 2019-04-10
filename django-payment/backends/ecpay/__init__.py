import datetime
import inspect
import math
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from requests import request
from ..base import PaymentBackend, InvalidInput, InvalidPayment
from .settings import settings
from .forms import ECPayAIOPNForm, ECPayAIOLookUpForm, ECPayPayForm
from .utils import decode_params


class ECPayAIOBackend(PaymentBackend):
    pn_form_class = ECPayAIOPNForm
    payment_form_class = ECPayPayForm
    backend_name = "ecpay_aio"

    def pn_details(self, form):
        # must pass form.is_valid before reaching here
        details = super(ECPayAIOBackend, self).pn_details(form)

        fee = math.floor((form.cleaned_data["PaymentTypeChargeFee"] +
                          form.handling_fee +
                          form.cleaned_data["TradeAmt"]*0.03)*100)/100.0

        details.update({
            "is_simulation": int(form.cleaned_data["SimulatePaid"]),
            "order_no": form.cleaned_data["MerchantTradeNo"],
            "payment_time": form.cleaned_data["PaymentDate"],
            "time_created": form.cleaned_data["TradeDate"],
            "payment_type": form.cleaned_data["PaymentType"],
            "payment_amount": form.cleaned_data["TradeAmt"],
            "additional_fee": fee,
        })
        return details

    def get_payment_form(self, **kwargs):
        kwargs['payment_type'] = 'ALL'
        form = super(ECPayAIOBackend, self).get_payment_form(**kwargs)
        if form.is_valid():
            return form
        else:
            raise ValidationError(
                "payment information is invalid, %s: %s\nerrors:%s" %
                (__name__,
                 inspect.currentframe().f_back.f_lineno,
                 form.errors))

    def get_ALL_payment_form(self, order,
                                form_class=ECPayPayForm):
        form = form_class(data={
            "MerchantTradeNo": order.order_no,
            "MerchantTradeDate": format_time(order.time_created),
            "PaymentType": "aio",
            "ChoosePayment": "ALL",
            "TotalAmount": order.payment_amount,
            "TradeDesc": order.description[0:200],
            "ItemName": order.title[0:200],
            "ReturnURL": self.pn_url(),
            "ChoosePayment": "Credit",
            "ClientBackURL": order.content_object.return_url,
            })
        return form

    def transaction_is_valid(self, pn_form):
        pn_form.is_valid()
        self.input_is_valid(pn_form)
        lookup_form = ECPayAIOLookUpForm(
            data={"MerchantTradeNo": pn_form.cleaned_data["MerchantTradeNo"]})

        self.input_is_valid(lookup_form)
        response = request("POST",
                           settings.LookUpURL,
                           data=lookup_form.cleaned_data)
        params = decode_params(response.content)
        status = params["TradeStatus"]
        pn_form.handling_fee = float(params["HandlingCharge"])
        if int(params["TradeAmt"]) != pn_form.cleaned_data["TradeAmt"]:
            raise ValidationError(
                "payment amount mismatch MerchantTradeNo: %s, %s: %s" %
                (params["MerchantTradeNo"],
                 __name__, inspect.currentframe().f_back.f_lineno))
        elif status != "1":
            raise ValidationError(
                "%s: %s, status %s %s" %
                (__name__, inspect.currentframe().f_back.f_lineno, status,
                 settings.TradeStatusCode[status]))
        return True

    @property
    def is_test(self):
        return super(ECPayAIOBackend, self).is_debug and settings.Test

    def valid_response(self):
        return HttpResponse("1|OK")

    def invalid_response(self, error_message):
        return HttpResponse("0|error"+error_message)
