import json
import time
import urllib

import scrapy
from django.utils.timezone import now

from gbb.main.models import Product


class WildberriesSpider(scrapy.Spider):
    name = "wildberries"
    allowed_domains = ["wildberries.ru"]
    domain = "www.wildberries.ru"
    card_domain = "card.wb.ru"
    scope = {}

    def _get_refer_product(self, article):
        return f"https://{self.domain}/catalog/{article}/detail.aspx?targetUrl=SP"

    def _get_product_url(self, article):
        url_data = {
            "spp": "0",
            "regions": "68,64,83,4,38,80,33,70,82,86,75,30,69,22,66,31,48,1,40,71",
            "pricemarginCoeff": "1.0",
            "reg": "0",
            "appType": "1",
            "emp": "0",
            "locale": "ru",
            "lang": "ru",
            "curr": "rub",
        }
        url_data["nm"] = article
        querystring = urllib.parse.urlencode(url_data, safe=",")
        return f"https://{self.card_domain}/cards/detail?{querystring}"

    def _request(
        self,
        url,
        parent_article=None,
        article=None,
        callback=None,
        referer=None,
    ):
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.88 Safari/537.36",
            "Referer": f"https://{self.domain}/",
        }
        if referer:
            headers["Referer"] = referer
        obj = scrapy.Request(
            url,
            method="GET",
            headers=headers,
            callback=callback,
            dont_filter=True,
        )
        obj.parent_article = parent_article
        obj.article = article
        return obj

    def _some_wait(self):
        time.sleep(self.sleep_time)

    def _full_scope_from_db(self):
        for product in Product.objects.all():
            self.scope[product.article] = {}
            for competitor in product.competitor_set.all():
                self.scope[product.article][competitor.article] = {}

    def start_requests(self):
        self.logger.info("start_requests")
        self.scope = {}
        self._full_scope_from_db()
        for (article, competitors) in self.scope.items():
            for (sub_article, competitor) in competitors.items():
                competitor["yielded"] = True
                yield self._request(
                    self._get_product_url(sub_article),
                    article,
                    sub_article,
                    callback=self.parse,
                    referer=self._get_refer_product(sub_article),
                )

    def _get_price_from_response(self, data):
        try:
            price = data["data"]["products"][0]["salePriceU"]
        except IndexError:
            price = None
        if price is not None:
            price = self._normalize_price(price)
        return price

    def _normalize_price(self, src_price):
        return int(src_price)

    def _get_product_obj_by_article(self, article):
        try:
            return Product.objects.get(article=article)
        except Product.DoesNotExist:
            self.logger.error(f"Product {article} not found")
        return None

    def _calc_new_price_by_avarage_stategy(self, src_prices):
        return int(round(sum(src_prices) / len(src_prices)))

    def _calc_new_price_by_edlp_stategy(self, src_prices):
        return int(src_prices[0] - (src_prices[0] / 100))

    def _on_competitors_all_parsed(self, acticle):
        prices = [
            competitor.get("price", None)
            for _, competitor in self.scope[acticle].items()
        ]
        prices = list(filter(None, prices))
        prices = sorted(prices)
        product_obj = self._get_product_obj_by_article(acticle)
        new_price = None
        available_competitors = True
        if len(prices) == 0:
            available_competitors = False
        if len(prices) > 0:
            if product_obj.pricing_strategy == Product.PricingStrategy.AVERAGE:
                new_price = self._calc_new_price_by_avarage_stategy(prices)
            if product_obj.pricing_strategy == Product.PricingStrategy.EDLP:
                new_price = self._calc_new_price_by_edlp_stategy(prices)
        product_obj.new_price = new_price
        product_obj.parsing_date = now()
        product_obj.available_competitors = available_competitors
        product_obj.save()

    def _test_competitors_all_parsed(self, acticle):
        parse_statuses = [
            competitor.get("parsed", False)
            for _, competitor in self.scope[acticle].items()
        ]
        if all(parse_statuses):
            return True
        return False

    def parse(self, response):
        parent_article = response.request.parent_article
        article = response.request.article
        self.scope[parent_article][article]["parsed"] = True
        if response.status == 404:
            self.scope[parent_article][article]["not_found"] = True
        if response.status == 200:
            data = json.loads(response.body)
            self.scope[parent_article][article]["found"] = True
            price = self._get_price_from_response(data)
            self.scope[parent_article][article]["price"] = price
        if self._test_competitors_all_parsed(parent_article):
            self._on_competitors_all_parsed(parent_article)

    def closed(self, reason):
        if reason == "finished":
            self.logger.info("success finished")
        self.logger.info(f"closed: {reason}")
