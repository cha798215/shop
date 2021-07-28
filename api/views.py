# -*- coding: utf-8 -*-

from django.db import transaction
from django.db.models import F, Sum
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.decorators import raise_if_not_vip, raise_if_out_of_stock, show_in_stock_hint
from api.serializers import OrderSerializer, ProductSerializer
from shopapp.models import Order, Product


class ProductViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(methods=["post"], detail=True, serializer_class=OrderSerializer)
    @raise_if_out_of_stock
    @raise_if_not_vip
    def order(self, request, *args, **kwargs):
        product = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            order = serializer.save(
                product=product,
                shop_id=product.shop_id,
                price=product.price,
            )
            product.stock_pcs = F("stock_pcs") - order.qty
            product.save(update_fields=["stock_pcs", "last_modified_at"])

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False)
    def top_three(self, request, *args, **kwargs):
        products = Product.objects.annotate(sold_count=Sum("orders__qty")).order_by(
            "-sold_count",
        )[:3]
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class OrderViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @show_in_stock_hint
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_destroy(self, order):
        with transaction.atomic():
            count, _order = order.delete()
            if count:
                order.product.stock_pcs = F("stock_pcs") + order.qty
                order.product.save(update_fields=["stock_pcs", "last_modified_at"])
