# django-payment
Simple payment system for my django project



## 安裝
### 方法1: pip 安裝
```bash
pip install git+https://github.com/pochangl/django-payment.git@v0.1.6
```

### 方法2: requirements.txt 安裝

在你的requirements.txt加入這行

```
git+git://github.com/pochangl/django-payment.git@v0.1.6
```

然後執行

```bash
pip install -r requirements.txt
```


## settings.py 檔

### 加入綠界後端


TEST 指使用測試環境
```python
INSTALLED_APPS = [
    ...,
    'django-payment',
]
PAYMENT_SETTINGS = {
    'BACKENDS': {
        'ECPAY': {
            'MERCHANT_ID': '2000132',
            'HASH_KEY': '5294y06JbISpM5x9',
            'HASH_IV': 'v77hoKGq4kWxNNIS',
            'EXPIRE_DATE': 7,
            'TEST': True,
            # 測試環境用 Tue, 實際環境用False
        }
    }
}
```


### 產品設定 settings.PAYMENT

```python
PAYMENT = {
    'BACKENDS': [
        # 使用的 BACKEND
        'payment.backends.ecpay.backend.ECPayAIOBackend',
    ],
    'PRODUCTS': [
        # 註冊產品英文名字
        'product.products.ProductOne',
    ],
    'SUCCESS_PIPE': [
        # 非必要
        # 無關產品本身的事件可以放這裡, 像是寄email通知之類的
        'product.pipes.increment',
    ]
}
```

## 建立第一個產品

### Book

```python
class Book(models.Model):
    book_title = models.CharField(max_length=16)
    book_description = models.CharField(max_length=16)
    book_price = models.PositiveIntegerField()

    is_active = models.BooleanField(default=False)

class BookOwner(models.Model):
    user = models.ForeignKey('auth.User')
    book = models.ForeignKey(Book)

```



## 取得產品資訊 (ProductSerializer)

這玩意會把 Book的名字, 價格, 跟描述取出來, 接下來的就丟給
基本上就 [名字, 價格, 描述] 3欄

```python

from rest_framework import serializers
from payment.products import ProductSerializer
from .models import Book


class BookProductSerializer(ProductSerializer):
    name = serializers.CharField(source='book_title')
    price = serializers.IntegerField(source='book_price')
    description = serializers.CharField(source='book_description')

    class Meta:
        model = Book
        # 產品的 Model

        fields = ('name', 'price', 'description')
        # 基本上就需要這 3 欄而己

```


## 產品Class

```python
from payment.products import Product


class BookProduct(Product):

    name = 'book'
    # 產品的英文名字, 盡量只用SlugField的字元吧, 未來會強制使用slug

    serializer_class = BookProductSerializer
    # 取得產品名字, 描述, 跟價錢的class


    return_view_name = 'return_page'
    # 付款完成後的訂單頁
    # reverse('return_page', kwargs={'pk': order.pk})


    view_name = 'product_info'
    # 產品頁面
    # reverse('product_info', kwargs={'pk': product.pk})

    class Meta:
        model = Book

    def apply(self, user, product):
        # 處理交易內容
        BookOwner.objects.create(user=user, book=product)

    def is_active(self):
        # 檢查產品是否可以購買
        return self.item.is_active and slef.item.book_price

```

## url.py

在最底層的url.py加入, 不要namespace

```python
urlpatterns = [
    ...,
    url(r'^pn/', include('payment.urls'))
]
```
