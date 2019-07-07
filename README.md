# django-payment
Simple payment system for my django project


## pip 安裝
```bash
pip install git+https://github.com/pochangl/django-payment.git@v0.1.6
```

## requirements.txt

在你的requirements.txt加入這行
```
git+git://github.com/pochangl/django-payment.git@v0.1.6
```

## 產品設定


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
