import scrapy


class PdfSpider(scrapy.Spider):
    name = "pdf"
    allowed_domains = ["docs.scrapy.org"]
    start_urls = ["https://docs.scrapy.org/en/latest/intro/tutorial.html"]

    def parse(self, response):
        
        pass
