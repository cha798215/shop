# -*- coding: utf-8 -*-
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import render

from shopapp.forms import OrderForm
from shopapp.models import Order, Product


def index(request, *args, **kwargs):
    if request.method == "POST":
        form = OrderForm(data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save()
                order.product.stock_pcs = F("stock_pcs") - order.qty
                order.product.save(update_fields=["stock_pcs", "last_modified_at"])
    else:
        form = OrderForm()

    top_three = Product.objects.annotate(sold_count=Sum("orders__qty")).order_by(
        "-sold_count",
    )[:3]

    return render(
        request,
        "shopapp/index.html",
        {
            "products": Product.objects.all(),
            "orders": Order.objects.all(),
            "form": form,
            "top_three": top_three,
        },
    )
