# -*- coding: utf-8 -*-
import scrapy
from RenderRequest import RenderRequest,Render

class ExampleSpider(scrapy.Spider):
    name = "example"

    start_urls = ('http://example.com',)


    def start_requests(self):
        for url in self.start_urls:
            yield RenderRequest(url,params={'example','example'},render=Render(),dont_filter=True)

    def parse(self, response):
        print(response)