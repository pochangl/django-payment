from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from .models import ProductBase
from .strategies import backends
from .utils import find_products

products = find_products()


class BackendField(forms.ChoiceField):
    def __init__(self, **kwargs):
        kwargs['choices'] = tuple(backends.items())
        super().__init__(**kwargs)


class BuyForm(forms.Form):
    backend = BackendField()
    content_type = forms.ModelChoiceField(queryset=ContentType.objects.all())
    object_id = forms.IntegerField(min_value=1)

    def clean_content_type(self):
        # make sure content type is a Product
        content_type = self.cleaned_data['content_type']
        if not issubclass(content_type, ProductBase):
            raise ValidationError('Content is not product type')
        return content_type

    def clean(self):
        data = self.clean()
        # make sure target product exists and is active
        model = data['content_type']
        pk = data['object_id']

        try:
            item = model.get(pk=pk)
        except model.DoesNotExist:
            raise ValidationError('Product does not exist')

        product_class = products[item]
        product = product_class(product=product, backend=data['backend'])

        if not product.is_active:
            raise ValidationError('Product is not active')

        data['content_object'] = item
        data['product'] = product
        return data
