# -*- coding: utf-8 -*-

from rest_framework import routers

from api import views as api_views

router = routers.SimpleRouter()
router.register(r"product", api_views.ProductViewSet)
router.register(r"order", api_views.OrderViewSet)
urlpatterns = router.urls
