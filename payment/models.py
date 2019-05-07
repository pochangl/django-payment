import calendar
from django.core.mail import send_mail
from django.core.signing import Signer
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.shortcuts import reverse
from django.utils.timezone import now


class TimeStampedModel(models.Model):
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PaymentErrorLog(TimeStampedModel):
    def __init__(self, *args, **kwargs):
            super(PaymentErrorLog, self).__init__(*args, **kwargs)

    def load_data(self, request, error_message):
            self.post = str(request.POST)
            self.get = str(request.GET)
            self.path = request.path
            self.encoding = request.encoding
            self.error_msg = error_message

    post = models.TextField(blank=True, null=True)
    get = models.TextField(blank=True, null=True)
    path = models.URLField(blank=True, null=True)
    encoding = models.TextField(blank=True, null=True)
    error_msg = models.TextField(blank=True, null=True)
    resolved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        send_mail("payment error",
                  str(vars(self)),
                  settings.SERVER_EMAIL,
                  [a[1] for a in settings.MANAGERS], fail_silently=False)
        return super(PaymentErrorLog, self).save()


class Order(TimeStampedModel):
    owner = models.ForeignKey('auth.User', related_name="orders")

    order_no = models.CharField(max_length=20, blank=True, unique=True,
                                null=True)
    backend = models.CharField(max_length=64, blank=True, null=True)

    payment_method = models.CharField(max_length=64)
    payment_amount = models.PositiveIntegerField()
    additional_fee = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=200, blank=True)
    payment_received = models.DateTimeField(blank=True, null=True)
    product_class = models.CharField(max_length=64)

    handled = models.BooleanField(default=False)

    # content
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def create_order_no(self):
        stamp = calendar.timegm(now().timetuple())
        self.order_no = '%dT%d' % (stamp, self.pk)


signer = Signer(salt="code")


class Code(TimeStampedModel):
    code = models.CharField(max_length=128, unique=True, null=True, default=None)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()

    @property
    def is_valid(self):
        return self.time_start <= now() < self.time_end

    def generate_code(self):
        if not self.pk:
            raise Exception('Model must be saved before automatic code generation')
        elif self.code is None:
            return signer.sign(self.pk)

    def post_save(self):
        code = self.generate_code()
        if code:
            self.code = code
            self.save()

    def __str__(self):
        return self.code

@receiver(post_save, sender=Code)
def code_generation(instance, created, *args, **kwargs):
    if created:
        instance.post_save()
