# -*- coding: utf-8 -*-
import csv

from django.core.management.base import BaseCommand
from django.db.models import Count, F, Sum
from django.utils import timezone

from shopapp.models import Shop


class Command(BaseCommand):
    """
    ./manage.py generate_daily_sales_report
    """

    def handle(self, *args, **options):
        self.main()

    def main(self):
        shops = Shop.objects.all()

        with open(f"daily_report_{timezone.now().date()}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Shop ID", "總銷售金額", "總銷售數量", "總訂單數量"])

            for shop in shops:
                data = shop.orders.annotate(
                    total_price=F("qty") * F("price"),
                ).aggregate(
                    total_sales_price=Sum("total_price"),
                    total_sales_qty=Sum("qty"),
                    total_orders_count=Count("id"),
                )
                writer.writerow(
                    [
                        shop.id,
                        data["total_sales_price"] or 0,
                        data["total_sales_qty"] or 0,
                        data["total_orders_count"] or 0,
                    ],
                )
