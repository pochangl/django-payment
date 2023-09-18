import inspect
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from requests import request
from ..base import PaymentBackend
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
        details.update({
            "is_simulation": int(form.cleaned_data["SimulatePaid"]),
            "order_no": form.cleaned_data["MerchantTradeNo"],
            "payment_time": form.cleaned_data["PaymentDate"],
            "time_created": form.cleaned_data["TradeDate"],
            "payment_type": form.cleaned_data["PaymentType"],
            "payment_amount": form.cleaned_data["TradeAmt"],
            "additional_fee": float(form.raw_data["HandlingCharge"]),
        })
        return details

    def get_payment_form(self, **kwargs):
        form = super(ECPayAIOBackend, self).get_payment_form(**kwargs)
        if form.is_valid():
            return form
        else:
            raise ValidationError(
                "payment information is invalid, %s: %s\nerrors:%s" %
                (__name__,
                 inspect.currentframe().f_back.f_lineno,
                 form.errors))

    def get_ALL_payment_form(self, order, product):
        form = ECPayPayForm(data={
            "MerchantTradeNo": order.order_no,
            "MerchantTradeDate": order.time_created,
            "PaymentType": "aio",
            "ChoosePayment": order.payment_method,
            "TotalAmount": order.payment_amount,
            "TradeDesc": order.description[0:200],
            "ItemName": order.title[0:200],
            "ReturnURL": self.pn_url(),
            "ChoosePayment": 'ALL',
            "ClientBackURL": product.get_return_url(order),
            "ItemURL": product.url,
        })
        return form

    def transaction_is_valid(self, pn_form):
        pn_form.is_valid()
        self.input_is_valid(pn_form)
        lookup_form = ECPayAIOLookUpForm(
            data={"MerchantTradeNo": pn_form.cleaned_data["MerchantTradeNo"]}
        )

        self.input_is_valid(lookup_form)
        response = request(
            "POST",
            settings.LookUpURL,
            data=lookup_form.cleaned_data
        )
        params = decode_params(response.content.decode('utf-8'))
        pn_form.raw_data = params
        status = params["TradeStatus"]

        if pn_form.cleaned_data['SimulatePaid']:
            return True
        elif int(params["TradeAmt"]) != pn_form.cleaned_data["TradeAmt"]:
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

    def valid_response(self):
        return HttpResponse("1|OK")

    def invalid_response(self, form):
        if int(form.data['RtnCode']) != 1:
            return HttpResponse('1|OK')
        else:
            return HttpResponse("0|error")
