import scrapy
from scrapy_selenium import SeleniumRequest
import re
import ast

class GamesSpider(scrapy.Spider):
    name = "games"
    allowed_domains = ["sandbox.oxylabs.io"]
    start_urls = ["https://sandbox.oxylabs.io/products"]

    # def parse(self, response):
        # Loop through each game card using XPath
        # for game in response.xpath('//div[contains(@class, "product-card")]'):
        #     yield {
        #         'title': game.xpath('.//h4[contains(@class, "title")]/text()').get(),
        #         'description': game.xpath('.//p[contains(@class, "description")]/text()').get(),
        #         'category': game.xpath('.//p[contains(@class, "category")]//span/text()').getall(),
        #         'price': game.xpath('.//div[contains(@class, "price-wrapper")]/text()').get(),
        #         # Add more fields if needed
        #     }
        # next_page_url = response.xpath('//ul/li/a[contains(@rel, "next")]/@href').extract_first()
        # if next_page_url:
        #     absolute_next_page_url = response.urljoin(next_page_url)
        #     yield scrapy.Request(absolute_next_page_url)
    
    def __init__(self, *args, **kwargs):
        super(GamesSpider, self).__init__(*args, **kwargs)
        self.game_urls = []  # List to store all game URLs

    def parse(self, response):
        # Collect all game detail URLs on current page
        for game in response.xpath('//div[contains(@class, "product-card")]'):
            # Findiing the href to the product detail page from the game card in home page
            relative_url = game.xpath('.//a[contains(@class, "card-header")]/@href').get()
            if relative_url:
                absolute_url = response.urljoin(relative_url)
                # self.game_urls.append(absolute_url)
                # Hitting a request as soon as the href link is found and parsing the details
                # Start requesting each game's detail page
                yield scrapy.Request(url=absolute_url, callback=self.parse_game_detail)
                self.logger.info(f"Parsing page: {absolute_url}")

        # Follow pagination
        next_page_url = response.xpath('//ul/li/a[contains(@rel, "next")]/@href').get()
        if next_page_url:
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse)


        '''The following method was used earlier, In this method all the games links were saved in list.
            Towards the end after all pagination is complete the details pages are hit one after another from the list.
            This needs for all the pagination to be complete to actually start parsing/scraping any details
        '''
        # for url in self.game_urls:
        #     yield scrapy.Request(url=url, callback=self.parse_game_detail) 

    def parse_game_detail(self, response):
        # Parseing the details from the game details page
        title = response.xpath('//title/text()').get()
        title = re.match(r"^(.*?)\s*\|", title)
        currency = response.xpath('//meta[@property="og:currency"]/@content').get(),
        price = response.xpath('//meta[@property="og:price"]/@content').get(),
        formatted_price = f"{currency} {price}" if price and currency else None
        yield {
            # 'title': title,
            'title': response.xpath('//h2[contains(@class, "title")]/text()').get(),
            'description': response.xpath('//p[contains(@class, "description")]//text()').get(),
            'category': ', '.join(ast.literal_eval(response.xpath('//meta[@property="og:genre"]/@content').get())),
            'price': response.xpath('//div[contains(@class, "price-wrapper")]/text()').get(),
            # 'price': formatted_price,
            'developer': response.xpath('//meta[@property="og:developer"]/@content').get(),
            'platform': ', '.join(ast.literal_eval(response.xpath('//meta[@property="og:platform"]/@content').get())),
            'game_type': response.xpath('//meta[@property="og:type"]/@content').get(),
            'image': response.xpath('//meta[@property="og:image"]/@content').get(),

            'availability': response.xpath('//p[contains(@class, "availability")]/text()').get(),
        }