#!/usr/bin/python
# -*- coding: UTF-8 -*-


from django.conf import settings as global_settings
import sys

production_settings = global_settings.PAYMENT['BACKENDS']['ECPAY']

class ECPaySettings():
    MerchantID = production_settings['MERCHANT_ID']
    HashKey = production_settings['HASH_KEY']
    HashIV = production_settings['HASH_IV']
    ExpireDays = production_settings['PAYMENT_EXPIRE_DAYS']
    TEST = False
    AioCheckOut_URL = "https://payment.ecpay.com.tw/Cashier/AioCheckOut/V5"
    LookUpURL = "https://payment.ecpay.com.tw/Cashier/QueryTradeInfo/V5"

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
        "10200050": "ECPayTradeID Error. ecpay 交易編號錯誤",
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

class ECPayTestSettings(ECPaySettings):
    AioCheckOut_URL = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"
    LookUpURL = "https://payment-stage.ecpay.com.tw/Cashier/QueryTradeInfo/V5"
    Test = True


if "test" in sys.argv or production_settings.get('test', False):
    settings = ECPayTestSettings
else:
    settings = ECPaySettings
