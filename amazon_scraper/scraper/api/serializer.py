from rest_framework import serializers
from scraper.models import Product, Brand

# ViewSets define the view behavior.
class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'asin', 'sku', 'brand', 'updated_at']

class BrandSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Brand
        fields = ['name', 'created_at']
