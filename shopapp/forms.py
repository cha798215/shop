# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from shopapp.models import Order, Product


class OrderForm(forms.ModelForm):
    vip = forms.BooleanField(required=False)
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(stock_pcs__gt=0),
        empty_label="Select Product",
    )

    class Meta:
        model = Order
        fields = [
            "product",
            "qty",
            "customer_id",
            "vip",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].widget.attrs.update(
            {"class": "form-control"},
        )
        self.fields["qty"].widget.attrs.update(
            {"class": "form-control", "placeholder": _("數量")},
        )
        self.fields["customer_id"].widget.attrs.update(
            {"class": "form-control"},
        )

    def clean(self):
        cleaned_data = self.cleaned_data
        product = cleaned_data.get("product")
        qty = cleaned_data.get("qty", 0)
        vip = cleaned_data.get("vip", False)

        if product:
            if product.stock_pcs < qty:
                self.add_error("qty", _("貨源不足"))

            if product.vip and not vip:
                self.add_error("vip", _("VIP 限定"))

        return cleaned_data

    def save(self, commit=True):
        order = super().save(commit=False)
        order.price = order.product.price

        if commit:
            order.save()
        return order
