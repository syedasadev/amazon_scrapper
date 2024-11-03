from django.contrib.auth.models import User
from django.urls import include, path
from .views import ProductViewSet, BrandViewSet
from rest_framework import routers

# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'product', ProductViewSet)
router.register(r'brand', BrandViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
]