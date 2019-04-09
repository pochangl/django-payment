#!/usr/bin/python
# -*- coding: UTF-8 -*-


from django.conf import settings as global_settings
import sys


class AllpaySettings():
    MerchantID = global_settings.ALLPAY_MERCHANT_ID
    HashKey = global_settings.ALLPAY_HASH_KEY
    HashIV = global_settings.ALLPAY_HASH_IV
    ExpireDays = global_settings.ALLPAY_PAYMENT_EXPIRE_DAYS
    TEST = False
    AioCheckOut_URL = global_settings.ALLPAY_AIO_CHECKOUT_URL
    LookUpURL = "https://payment.allpay.com.tw/Cashier/QueryTradeInfo"

    DateTimeFormats = ['%Y/%m/%d %H:%M:%S']
    PaymentType = "aio"
    PaymentChoices = (
        ("Credit", "信用卡"),
        # ("WebATM","網路 ATM"),
        ("ATM", "自動櫃員機"),
        ("CVS", "超商代碼"),
        # ("BARCODE","超商條碼"),
        # ("Alipay","支付寶"),
        # ("Tenpay","財付通"),
        # ("TopUpUsed","儲值消費"),
    )
    ResponsePaymentTypePrefixes = (r"^Credit",
                                   r"^ATM",
                                   r"^CVS",)
    TradeStatusCode = {
        "1": "Succeeded 成功",
        "2": "Create Trade Successed. 建立訂單成功",
        "10200001": "Can not use trade service. 無法使用此服務",
        "10200002": "Trade has been updated before. 交易已處理",
        "10200003": "Trade Status Error. 交易狀態錯誤",
        "10200005": "Price Format Error. 金額格式錯誤",
        "10200007": "ItemURL Format Error. URL 格式錯誤",
        "10200050": "AllPayTradeID Error. AllPay 交易編號錯誤",
        "10200051": "MerchantID Error. 廠商編號錯誤",
        "10200052": "MerchantTradeNo Error. 廠商交易編號錯誤",
        "10100001": "IP Access Denied. IP 拒絕存取",
        "10100050": "Parameter Error.",
        "10100054": "Trading Number Repeated. 交易編號重覆",
        "10200073": "CheckMacValue Error 檢查碼錯誤",
        "10100055": "Create Trade Fail. 建立訂單失敗",
        "10100058": "Pay Fail. 付款失敗",
        "10100059": "Trading Number cannot Be Found. 找不到訂單編號",
    }


class AllpayTestSettings(AllpaySettings):
    MerchantID = global_settings.ALLPAY_TEST_MERCHANT_ID
    HashKey = global_settings.ALLPAY_TEST_HASH_KEY
    HashIV = global_settings.ALLPAY_TEST_HASH_IV
    AioCheckOut_URL = global_settings.ALLPAY_TEST_AIO_CHECKOUT_URL
    LookUpURL = "http://payment-stage.allpay.com.tw/Cashier/QueryTradeInfo"
    Test = True


if global_settings.ALLPAY_TEST or "test" in sys.argv:
    settings = AllpayTestSettings
else:
    settings = AllpaySettings
