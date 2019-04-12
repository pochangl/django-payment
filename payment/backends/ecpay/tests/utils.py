from django.test import TestCase
from ..utils import generate_CheckMacValue


class TestUtils(TestCase):
    def test_generate_CheckMacValue(self):
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

        mac = generate_CheckMacValue(dictionary=data, key=key, iv=iv)

        self.assertEqual(mac, 'CFA9BDE377361FBDD8F160274930E815D1A8A2E3E80CE7D404C45FC9A0A1E407')