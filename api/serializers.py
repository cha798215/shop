# -*- coding: utf-8 -*-
from rest_framework import serializers

from shopapp.models import Order, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "shop_id",
            "stock_pcs",
            "price",
            "vip",
        ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "customer_id",
            "product_id",
            "shop_id",
            "qty",
            "price",
        ]
        read_only_fields = ["shop_id", "price"]
