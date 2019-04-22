def increment(product, **kwargs):
    product.item.count += 1
    product.item.save()
