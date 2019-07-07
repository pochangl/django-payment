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

## 加入綠界後端


TEST 指使用測試環境
```python
PAYMENT_SETTINGS = {
    'BACKENDS': {
        'ECPAY': {
            'MERCHANT_ID': '2000132',
            'HASH_KEY': '5294y06JbISpM5x9',
            'HASH_IV': 'v77hoKGq4kWxNNIS',
            'EXPIRE_DATE': 7,
            'TEST': True
        }
    }
}
```


## 產品設定 settings.PAYMENT

```python
PAYMENT = {
    'BACKENDS': [
        'payment.backends.ecpay.backend.ECPayAIOBackend'
    ],
    'PRODUCTS': [
        'product.products.ProductOne'
    ],
    'SUCCESS_PIPE': [
        'product.pipes.increment'
    ]
}
```

BACKEND - <class list>
    backend的位置

PRODUCTS - <class list>
    產品的Handler, 

SUCCESS_PIPE - <class list>
    產品處理完後的動作



## 產品Class

```
from payment.products import Product

class ProductOne(Product):
    name = 'product_one'
    serializer_class = ProductModelSerializer
    return_view_name = 'return_page'
    view_name = 'product_info'

    class Meta:
        model = ProductModel

    def apply(self, user):
        item = self.item
        item.buyers.add(user)

    def is_active(self):
        return super().is_active() and self.item.is_active

```
