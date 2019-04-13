from rest_framework.serializers import ModelSerializer


class ProductSerializer(ModelSerializer):
    @property
    def data(self):
        # transform to corresponded field
        data = super().data()
        return {
            'title': data['name'],
            'payment_amount': data['price'],
            'description': data['description'],
            'content_object': self.instance
        }
