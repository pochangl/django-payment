import datetime
from django.test import TestCase
from ..forms import ECPayPayForm
from ..utils import timezone
from ..settings import settings


class TestPayAllForm(TestCase):
    data = {
        'ChoosePayment': 'ALL',
        'ItemName': 'Apple iphone 7 手機殼',
        'MerchantID': '2000132',
        'MerchantTradeDate': '2013/03/12 15:30:23',
        'MerchantTradeNo': 'ecpay20130312153023',
        'PaymentType': 'aio',
        'ReturnURL': 'https://www.ecpay.com.tw/receive.php',
        'TotalAmount': 1000,
        'TradeDesc': '促銷方案',
        'ClientBackURL': 'https://example.com',
        'ExpireDate': 7,
    }
    cmv = '1565694EB29C358B1C7B4FE2088A56B046F620BB9B405DE93FA41D3C31A510CD'

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
        fields = ('MerchantID', 'EncryptType', 'ExpireDate', 'MerchantTradeDate')
        for field in fields:
            data.pop(field, None)
        form = ECPayPayForm(data=data)
        self.assertTrue(form.is_valid())
        for field in fields:
            self.assertTrue(form.cleaned_data[field])

        self.assertEqual(form.cleaned_data['MerchantID'], self.data['MerchantID'])
        self.assertEqual(form.cleaned_data['EncryptType'], 1)
        self.assertEqual(form.cleaned_data['ExpireDate'], 7)
