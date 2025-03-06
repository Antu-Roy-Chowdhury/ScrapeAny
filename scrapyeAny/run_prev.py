import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import json
import csv
import os
import zipfile


class MySpider(scrapy.Spider):
    name = "myspider"
    
    def _init_(self, url=None, data_types = None, *args, **kwargs):
        super(MySpider, self)._init_(*args, **kwargs)
        self.start_urls = [url]
        self.data_types = data_types or []
        self.output_dir = "ScarpedData"

    
    def parse(self, response):
        self.logger.info("Visited %s to Scraping", response.url)

        result = {}

        if "title" in self.data_types:
            result["title"] = response.css("title::text").getall()
            self.save_to_file("title", "title.txt")

        if "images" in self.data_types:
            images = response.css("img::attr(src)").getall()
            result["images"] = images
            for i, image in enumerate(images):
                self.save_to_file(f"image_{i}.jpg", image)

        if "links" in self.data_types:
            result["links"] = response.css("a::attr(href)").getall()
            self.save_to_file("links", "links.txt")

        if "paragraphs" in self.data_types:
            result["paragraphs"] = response.css("p::text").getall()
            self.save_to_file("paragraphs", "paragraphs.txt")

        if "spans" in self.data_types:
            result["spans"] = response.css("span::text").getall()
            self.save_to_file("spans", "spans.txt")

        if "pdfs" in self.data_types:
            result["pdfs"] = response.css("a[href$='.pdf']::attr(href)").getall()
            for i, pdf in enumerate(result["pdfs"]):
                self.save_to_file(f"pdf_{i}.pdf", pdf)

        if "docs" in self.data_types:
            result["docs"] = response.css("a[href$='.doc']::attr(href)").getall()
            for i, doc in enumerate(result["docs"]):
                self.save_to_file(f"doc_{i}.docx", doc)

        if "videos" in self.data_types:
            result["videos"] = response.css("video source::attr(src), source[type^='video']::attr(src), a[href$='mp4']::attr(href),a[href$='webm']::attr(href)").getall()
            for i, video in enumerate(result["videos"]):
                self.save_to_file(f"video_{i}.mp4", video)
        if "audios" in self.data_types:
            result["audios"] = response.css("audio source::attr(src), source[type^='audio']::attr(src), a[href$='mp3']::attr(href),a[href$='wav']::attr(href)").getall()
            for i, audio in enumerate(result["audios"]):
                self.save_to_file(f"audio_{i}.mp3", audio)
        if "tables" in self.data_types:
            result["tables"] = response.css("table")
            for table_index, table in enumerate(result["tables"]):
                table_data = []
                for row in table.css("tr"):
                    row_data = []
                    for cell in row.css("td, th"):
                        row_data.append(cell.css("::text").get(default="").strip())
                    table_data.append(row_data)
                self.save_table(f"table_{table_index}.csv", table_data)


        if "quotes" in self.data_types:
            result["quotes"] = response.css("blockquote::text").getall()
            self.save_to_file("quotes", "quotes.txt")
        if "headings" in self.data_types:
            result["headings"] = response.css("h1::text, h2::text, h3::text, h4::text, h5::text, h6::text").getall()
            self.save_to_file("headings", "headings.txt")

        if "lists" in self.data_types:
            result["lists"] = response.css("ul, ol").getall()   
            self.save_to_file("lists", "lists.txt")
        
        if "personal" in self.data_types:

            result["name"] = response.css("span.name::text").get(default="").strip()
            result["email"] = response.css("span.email::text").get(default="").strip()
            result["phone"] = response.css("span.phone::text").get(default="").strip()
            self.save_to_file("personal", "personal.json")
        
        yield result
    
    def save_table(self, filename, table_data):
        with open(os.path.join(self.output_dir, filename), "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(table_data)
        
    
def run_spider(url, data_types, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    process = CrawlerProcess(get_project_settings())
    process.crawl(MySpider, url=url, data_types=data_types, output_dir=output_dir)
    process.start()

if __name__ == "__main__":
    url = input("Enter URL to Scrap Data: ")
    options = {
        '1': 'title',
        '2': 'images',
        '3': 'links',
        '4': 'paragraphs',
        '5': 'spans',
        '6': 'pdfs',
        '7': 'docs',
        '8': 'videos',
        '9': 'audios',
        '10': 'tables',
        '11': 'quotes',
        '12': 'headings',
        '13': 'lists',
        '14': 'personal'
    }
    for key, value in options.items():
        print(f"{key}: {value.capitalize()}")
    selected_options = input("Enter Data Types to Scrap (comma separated): ").split(",")
    data_types = [options[option] for option in selected_options]
    output_dir = "ScarpedData"
    run_spider(url, data_types, output_dir)

    # Zip the output directory
    with zipfile.ZipFile(f"{output_dir}.zip", "w") as zf:
        for dirname, subdirs, files in os.walk(output_dir):
            zf.write(dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename))
    
    print(f"Data Scraped Successfully and saved in {output_dir}.zip")