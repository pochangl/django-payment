import datetime
import pytz
from django.test import TestCase
from ..utils import generate_CheckMacValue, format_time
from ..settings import settings


class TestUtils(TestCase):
    data = {
        'ChoosePayment': 'ALL',
        'EncryptType' : '1',
        'ItemName': 'Apple iphone 7 手機殼',
        'MerchantID': '2000132',
        'MerchantTradeDate': '2013/03/12 15:30:23',
        'MerchantTradeNo': 'ecpay20130312153023',
        'PaymentType': 'aio',
        'ReturnURL': 'https://www.ecpay.com.tw/receive.php',
        'TotalAmount': '1000',
        'TradeDesc': '促銷方案',
    }
    key = '5294y06JbISpM5x9'
    iv = 'v77hoKGq4kWxNNIS'

    def test_generate_CheckMacValue(self):
        mac = generate_CheckMacValue(dictionary=self.data, key=self.key, iv=self.iv)

        self.assertEqual(mac, 'CFA9BDE377361FBDD8F160274930E815D1A8A2E3E80CE7D404C45FC9A0A1E407')

    def test_datetime(self):
        timezone = pytz.timezone('Asia/Taipei')
        data = self.data.copy()
        time = datetime.datetime.strptime(data['MerchantTradeDate'], settings.DateTimeFormat)
        time = timezone.localize(time)
        data['MerchantTradeDate'] = time

        mac = generate_CheckMacValue(dictionary=data, key=self.key, iv=self.iv)

        self.assertEqual(mac, 'CFA9BDE377361FBDD8F160274930E815D1A8A2E3E80CE7D404C45FC9A0A1E407')

    def test_timezone(self):
        timezone = pytz.timezone('Asia/Taipei')
        data = self.data.copy()
        time = datetime.datetime.strptime(data['MerchantTradeDate'], settings.DateTimeFormat)
        data['MerchantTradeDate'] = timezone.localize(time)

        mac = generate_CheckMacValue(dictionary=data, key=self.key, iv=self.iv)

        self.assertEqual(mac, 'CFA9BDE377361FBDD8F160274930E815D1A8A2E3E80CE7D404C45FC9A0A1E407')


class TestFormatTime(TestCase):
    def test_local_format(self):
        timezone = pytz.timezone('Asia/Taipei')
        time = datetime.datetime(year=2000, month=1, day=1, hour=0, minute=0, second=0)
        time = timezone.localize(time)
        time_str = format_time(time)
        self.assertEqual(time_str, '2000/01/01 00:00:00')

    def test_utc_time(self):
        time = datetime.datetime(year=2000, month=1, day=1, hour=0, minute=0, second=0).replace(tzinfo=pytz.utc)
        time_str = format_time(time)
        self.assertEqual(time_str, '2000/01/01 08:00:00')
