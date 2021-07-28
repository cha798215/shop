# -*- coding: utf-8 -*-
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from model_bakery import baker


class ProductListTest(TestCase):
    def setUp(self):
        super().setUp()
        self.shop = baker.make("shopapp.Shop")
        baker.make("shopapp.Product", shop=self.shop, _quantity=4)
        self.url = reverse("api:product-list")

    def test_ok(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        content = resp.json()
        self.assertEqual(len(content), 4)


class ProductOrderTest(TestCase):
    def setUp(self):
        super().setUp()
        self.shop = baker.make("shopapp.Shop")
        self.product = baker.make("shopapp.Product", shop=self.shop, stock_pcs=10)
        self.url = reverse("api:product-order", args=[self.product.id])
        self.data = {
            "customer_id": 12345,
            "qty": 10,
        }

    def test_ok(self):
        resp = self.client.post(self.url, self.data)
        self.assertEqual(resp.status_code, 201)
        content = resp.json()
        self.assertEqual(content["customer_id"], self.data["customer_id"])
        self.assertEqual(content["qty"], self.data["qty"])
        self.assertEqual(content["product_id"], self.product.id)
        self.assertEqual(content["shop_id"], self.shop.id)
        self.assertEqual(content["price"], self.product.price)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_pcs, 0)

    def test_fail_with_vip_required(self):
        self.product.vip = True
        self.product.save(update_fields=["vip"])

        resp = self.client.post(self.url, self.data)
        self.assertEqual(resp.status_code, 400)
        content = resp.json()
        self.assertEqual(content["detail"], _("VIP 限定"))

    def test_fail_with_out_of_stock(self):
        self.data["qty"] = 100
        resp = self.client.post(self.url, self.data)
        self.assertEqual(resp.status_code, 400)
        content = resp.json()
        self.assertEqual(content["detail"], _("貨源不足"))


class ProductTopThreeTest(TestCase):
    def setUp(self):
        super().setUp()
        self.shop = baker.make("shopapp.Shop")
        self.product1 = baker.make("shopapp.Product", shop=self.shop)
        self.product2 = baker.make("shopapp.Product", shop=self.shop)
        self.product3 = baker.make("shopapp.Product", shop=self.shop)
        self.product4 = baker.make("shopapp.Product", shop=self.shop)

        baker.make(
            "shopapp.Order",
            product=self.product1,
            qty=100,
            _quantity=10,
        )  # 1000
        baker.make("shopapp.Order", product=self.product2, qty=10, _quantity=10)  # 100
        baker.make("shopapp.Order", product=self.product3, qty=100, _quantity=9)  # 900
        baker.make("shopapp.Order", product=self.product4, qty=95, _quantity=10)  # 950

        self.url = reverse("api:product-top-three")

    def test_ok(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        content = resp.json()
        self.assertEqual(len(content), 3)

        product_ids = [product["id"] for product in content]
        self.assertListEqual(
            product_ids,
            [self.product1.id, self.product4.id, self.product3.id],
        )


class OrderDestroyTest(TestCase):
    def setUp(self):
        super().setUp()
        self.product = baker.make("shopapp.Product", stock_pcs=10)
        self.order = baker.make("shopapp.Order", product=self.product, qty=3)
        self.url = reverse("api:order-detail", args=[self.order.id])

    def test_ok(self):
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 204)

    def test_ok_with_in_stock_hint(self):
        self.product.stock_pcs = 0
        self.product.save(update_fields=["stock_pcs"])
        resp = self.client.delete(self.url)
        self.assertEqual(resp.status_code, 200)
        content = resp.json()
        self.assertEqual(content["detail"], _("商品到貨"))
