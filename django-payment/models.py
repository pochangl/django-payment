from django.db import models
from custom.models import TimeStampedModel
from django.core.mail import send_mail
from django.conf import settings


class PreservedTupleMixin(object):
    def delete(self, *args, **kwargs):
        class PreservedTuple(Exception):
            pass
        raise PreservedTuple("The tuple ought not to be delete")


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


class Order(PreservedTupleMixin, custom_models.TimeStampedModel):
    objects = managers.OrderManager()

    order_no = models.CharField(max_length=20, blank=True, unique=True,
                                null=True)
    backend = models.CharField(max_length=64, blank=True, null=True)
    owner = models.ForeignKey('auth.User', related_name="orders")
    coupon = models.ForeignKey(Coupon, null=True, blank=True, default=None,
                               related_name="orders")
    payment_amount = models.PositiveIntegerField()
    commission = models.PositiveIntegerField(default=0)
    additional_fee = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=200, blank=True)
    payment_received = models.DateTimeField(blank=True, null=True)

    def clean(self):
        desc = "%s-%s: %s" % (self.course.title, self.course.title_ext,
                              self.package.description)
        setattr(self, "description", desc[0:200])
        setattr(self, "title", self.course.title[0:200])
        setattr(self, "order_no", order_no_generator(self))

    @property
    def user_return_url(self):
        return reverse('course_view', kwargs={"course_slug": self.course.slug})

    def save(self, *args, **kwargs):
        ret = super(Order, self).save(*args, **kwargs)

        if self.coupon and self.payment_received:
            # update self.coupon.used
            self.coupon.save()
        return ret

    @classmethod
    def setup_free_order(cls, **kwargs):
        initial_val = {
            "backend": None,
            "payment_amount": 0,
        }
        initial_val.update(kwargs)
        order = Order.objects.create(**initial_val)
        order.full_clean()
        order.save(force_update=True)
        order.order_no = "free%s" % order.id
        order.save()

        details = {"order_no": "%s" % order.order_no,
                   "payment_amount": 0,
                   "additional_fee": 0,
                   "is_simulation": False,
                   "payment_type": "free"}
        receive_payment(details)
