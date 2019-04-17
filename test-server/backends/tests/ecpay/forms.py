import datetime
from django.test import TestCase
from payment.backends.ecpay.forms import ECPayPayForm
from payment.backends.ecpay.utils import timezone
from payment.backends.ecpay.settings import settings


class TestPayAllForm(TestCase):
    data = {
        'ChoosePayment': 'ALL',
        'ItemName': 'Apple iphone 7 手機殼',
        'MerchantID': '2000132',
        'MerchantTradeDate': '2013/03/12 15:30:23',
        'MerchantTradeNo': 'ecpay20130312153023',
        'PaymentType': 'aio',
        'ReturnURL': 'https://example.com',
        'TotalAmount': 1000,
        'TradeDesc': '促銷方案',
        'ClientBackURL': 'https://example.com',
        'ExpireDate': 7,
        'ItemURL': 'https://example.com',
    }
    cmv = '935B75AA25C207F8C415122DC3BA5058DC7CF410DF25D4B7F8C0D5714FCD4AF1'

    def setUp(self):
        self.input_data = data = self.data.copy()
        time = datetime.datetime.strptime(data['MerchantTradeDate'], settings.DateTimeFormat)
        data['MerchantTradeDate'] = timezone.localize(time)

    def test_cmv(self):
        form = ECPayPayForm(data=self.input_data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['CheckMacValue'], self.cmv)

        expected = self.data.copy()
        expected['CheckMacValue'] = self.cmv
        expected['EncryptType'] = 1
        self.assertEqual(expected, form.cleaned_data)

    def test_auto_field_generation(self):
        data = self.input_data.copy()
        fields = ('MerchantID', 'EncryptType', 'ExpireDate')
        for field in fields:
            data.pop(field, None)
        form = ECPayPayForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        for field in fields:
            self.assertTrue(form.cleaned_data[field])

        self.assertEqual(form.cleaned_data['MerchantID'], self.data['MerchantID'])
        self.assertEqual(form.cleaned_data['EncryptType'], 1)
        self.assertEqual(form.cleaned_data['ExpireDate'], 7)
