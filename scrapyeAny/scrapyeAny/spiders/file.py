import scrapy


class FileSpider(scrapy.Spider):
    name = "file"
    allowed_domains = ["www.getpdf.com"]
    start_urls = ["https://www.getpdf.com/download.html"]

    def parse(self, response):
        pass
