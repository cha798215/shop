# -*- coding: utf-8 -*-
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Shop(models.Model):
    """館別"""

    name = models.CharField(verbose_name=_("館別名稱"), max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("館別")
        verbose_name_plural = _("館別")

    def __str__(self):
        return self.name


class Product(models.Model):
    """商品"""

    name = models.CharField(verbose_name=_("商品名稱"), max_length=50)
    shop = models.ForeignKey(
        Shop,
        related_name="products",
        on_delete=models.CASCADE,
        verbose_name=_("館別"),
    )
    stock_pcs = models.PositiveIntegerField(verbose_name=_("商品庫存數量"), default=0)
    price = models.PositiveIntegerField(verbose_name=_("商品單價"))
    vip = models.BooleanField(verbose_name=_("VIP 限定"), default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("商品")
        verbose_name_plural = _("商品")

    def __str__(self):
        return f"{self.shop.name}：{self.name}"


class Order(models.Model):
    """訂單"""

    customer_id = models.PositiveIntegerField(verbose_name=_("顧客 ID"))
    shop = models.ForeignKey(
        Shop,
        related_name="orders",
        on_delete=models.CASCADE,
        verbose_name=_("館別"),
    )
    product = models.ForeignKey(
        Product,
        related_name="orders",
        on_delete=models.CASCADE,
        verbose_name=_("商品"),
    )
    qty = models.PositiveSmallIntegerField(
        verbose_name=_("購買數量"),
        default=1,
        validators=[MinValueValidator(1)],
    )
    price = models.PositiveIntegerField(verbose_name=_("商品單價"))

    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("訂單")
        verbose_name_plural = _("訂單")

    def __str__(self):
        return f"{self.customer_id}：{self.product.name} * {self.qty}"
