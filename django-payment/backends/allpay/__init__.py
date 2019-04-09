
from payment.backends.base import PaymentBackend, InvalidInput, InvalidPayment
from payment.backends.allpay.forms import AllPayAIOPNForm, \
    AllPayAIOLookUpForm, AllPayCreditForm, AllPayCVSForm, AllPayATMForm
from payment.backends.allpay.utils import decode_params
from django.http import HttpResponse
from requests import request
from payment.backends.allpay.settings import settings
from django.core.exceptions import ValidationError
import datetime
import inspect
import math


class AllPayAIOBackend(PaymentBackend):
    pn_form_class = AllPayAIOPNForm
    # payment_form_class = AllPayPayForm
    backend_name = "allpay_aio"

    def pn_details(self, form):
        # must pass form.is_valid before reaching here
        details = super(AllPayAIOBackend, self).pn_details(form)

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

    def get_payment_form(self, *args, **kwargs):
        form = super(AllPayAIOBackend, self).get_payment_form(*args, **kwargs)
        if form.is_valid():
            return form
        else:
            raise ValidationError(
                "payment information is invalid, %s: %s\nerrors:%s" %
                (__name__,
                 inspect.currentframe().f_back.f_lineno,
                 form.errors))

    def get_Credit_payment_form(self, order_no, title, payment_amount,
                                description, time_created, user_return_url,
                                form_class=AllPayCreditForm):
        form = form_class(data={
            "MerchantTradeNo": order_no,
            "MerchantTradeDate": time_created,
            "PaymentType": "aio",
            "TotalAmount": payment_amount,
            "TradeDesc": description[0:200],
            "ItemName": title[0:200],
            "ReturnURL": self.pn_url(),
            "ChoosePayment": "Credit",
            "ClientBackURL": user_return_url,
            })
        return form

    def get_CVS_payment_form(self, order_no, title, payment_amount,
                             description, time_created,
                             user_return_url,
                             form_class=AllPayCVSForm):
        form = form_class(data={
            "MerchantTradeNo": order_no,
            "MerchantTradeDate": time_created,
            "PaymentType": "aio",
            "TotalAmount": payment_amount,
            "TradeDesc": description[0:200],
            "ItemName": title[0:200],
            "ReturnURL": self.pn_url(),
            "ChoosePayment": "CVS",
            "ClientBackURL": user_return_url,
            "Desc_1": title[0:20],
            "Desc_2": title[20:40],
            "Desc_3": title[40:60],
            "Desc_4": title[60:80],
            })
        return form

    def get_ATM_payment_form(self, order_no, title, payment_amount,
                             description, time_created, user_return_url,
                             form_class=AllPayATMForm):
        form = form_class(data={
            "MerchantTradeNo": order_no,
            "MerchantTradeDate": time_created,
            "PaymentType": "aio",
            "TotalAmount": payment_amount,
            "TradeDesc": description[0:200],
            "ItemName": title[0:200],
            "ReturnURL": self.pn_url(),
            "ChoosePayment": "ATM",
            "ClientBackURL": user_return_url,
            "ExpireDate": settings.ExpireDays,
            })
        return form

    def transaction_is_valid(self, pn_form):
        pn_form.is_valid()
        self.input_is_valid(pn_form)
        lookup_form = AllPayAIOLookUpForm(
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
        return super(AllPayAIOBackend, self).is_debug and settings.Test

    def valid_response(self):
        return HttpResponse("1|OK")

    def invalid_response(self, error_message):
        return HttpResponse("0|error"+error_message)
