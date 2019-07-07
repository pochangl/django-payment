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

```bash
然後執行pip install -r requirements.txt
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
