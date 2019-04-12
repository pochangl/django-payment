from django.db import models

from payment.models import TimeStampedModel


class ECPayReceive(TimeStampedModel):
    MerchantID = models.CharField(max_length=10)
    MerchantTradeNo = models.CharField(max_length=20)
    RtnCode = models.IntegerField()
    RtnMsg = models.CharField(max_length=200, blank=True)
    TradeNo = models.CharField(max_length=20)
    TradeAmt = models.IntegerField()
    PaymentDate = models.DateTimeField()
    PaymentType = models.CharField(max_length=20)
    PaymentTypeChargeFee = models.FloatField()
    TradeDate = models.DateTimeField()
    SimulatePaid = models.IntegerField()
    CheckMacValue = models.CharField(max_length=64)
