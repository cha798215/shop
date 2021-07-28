# -*- coding: utf-8 -*-
import functools

from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ParseError


def raise_if_out_of_stock(func):
    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        product = self.get_object()

        try:
            order_qty = int(request.data.get("qty", "0"))
        except ValueError:
            pass
        else:
            if product.stock_pcs < order_qty:
                raise ParseError(_("貨源不足"))

        return func(self, request, *args, **kwargs)

    return wrapper


def raise_if_not_vip(func):
    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        product = self.get_object()
        order_vip = request.data.get("vip", "false").lower() == "true"
        if product.vip and not order_vip:
            raise ParseError(_("VIP 限定"))

        return func(self, request, *args, **kwargs)

    return wrapper


def show_in_stock_hint(func):
    @functools.wraps(func)
    def wrapper(self, request, *args, **kwargs):
        order = self.get_object()
        product = order.product

        show_hint = False
        if product.stock_pcs == 0:
            show_hint = True

        response = func(self, request, *args, **kwargs)
        if show_hint:
            response.status_code = status.HTTP_200_OK
            response.data = {"detail": _("商品到貨")}

        return response

    return wrapper
