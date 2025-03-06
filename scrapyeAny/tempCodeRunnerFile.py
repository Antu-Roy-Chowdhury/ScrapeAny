import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import json
import csv
import os
import zipfile


class MySpider(scrapy.Spider):
    name = "myspider"

    def __init__(self, url=None, data_types=None, output_dir=None, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.start_urls = [url] if url else []
        self.data_types = data_types or []
        self.output_dir = output_dir or "ScrapedData"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def parse(self, response):
        self.logger.info(f"Visited {response.url} to scrape data")
        result = {}

        if "title" in self.data_types:
            result["title"] = response.css("title::text").getall()
            self.save_to_file("title.txt", result["title"])

        if "images" in self.data_types:
            images = response.css("img::attr(src)").getall()
            result["images"] = images
            # Download images through th pipeline
            for image_index, image_url in enumerate(images):
                image_url = response.urljoin(image_url)
                image_name = image_url.split("/")[-1]
                image_path = os.path.join(self.output_dir, image_name)
                self.save_to_file(f"image_{image_index}.jpg", image_url)
                

        if "links" in self.data_types:
            result["links"] = response.css("a::attr(href)").getall()
            self.save_to_file("links.txt", result["links"])

        if "paragraphs" in self.data_types:
            result["paragraphs"] = response.css("p::text").getall()
            self.save_to_file("paragraphs.txt", result["paragraphs"])

        if "spans" in self.data_types:
            result["spans"] = response.css("span::text").getall()
            self.save_to_file("spans.txt", result["spans"])

        if "pdfs" in self.data_types:
            result["pdfs"] = response.css("a[href$='.pdf']::attr(href)").getall()
            self.save_to_file("pdfs.txt", result["pdfs"])

        if "docs" in self.data_types:
            result["docs"] = response.css("a[href$='.doc']::attr(href)").getall()
            self.save_to_file("docs.txt", result["docs"])

        if "videos" in self.data_types:
            result["videos"] = response.css("video source::attr(src), source[type^='video']::attr(src), a[href$='.mp4']::attr(href), a[href$='.webm']::attr(href)").getall()
            for video_index, video_url in enumerate(result["videos"]):
                video_url = response.urljoin(video_url)
                video_name = video_url.split("/")[-1]
                video_path = os.path.join(self.output_dir, video_name)
                self.save_to_file(f"video_{video_index}.mp4", video_url)


        if "audios" in self.data_types:
            result["audios"] = response.css("audio source::attr(src), source[type^='audio']::attr(src), a[href$='.mp3']::attr(href), a[href$='.wav']::attr(href)").getall()
            for audio_index, audio_url in enumerate(result["audios"]):
                audio_url = response.urljoin(audio_url)
                audio_name = audio_url.split("/")[-1]
                audio_path = os.path.join(self.output_dir, audio_name)
                self.save_to_file(f"audio_{audio_index}.mp3", audio_url)

        if "tables" in self.data_types:
            result["tables"] = response.css("table")
            for table_index, table in enumerate(result["tables"]):
                table_data = []
                for row in table.css("tr"):
                    row_data = [cell.css("::text").get(default="").strip() for cell in row.css("td, th")]
                    table_data.append(row_data)
                self.save_table(f"table_{table_index}.csv", table_data)

        if "quotes" in self.data_types:
            result["quotes"] = response.css("blockquote::text").getall()
            self.save_to_file("quotes.txt", result["quotes"])

        if "headings" in self.data_types:
            result["headings"] = response.css("h1::text, h2::text, h3::text, h4::text, h5::text, h6::text").getall()
            self.save_to_file("headings.txt", result["headings"])

        if "lists" in self.data_types:
            result["lists"] = response.css("ul, ol").getall()
            self.save_to_file("lists.txt", result["lists"])

        if "personal" in self.data_types:
            result["name"] = response.css("span.name::text").get(default="").strip()
            result["email"] = response.css("span.email::text").get(default="").strip()
            result["phone"] = response.css("span.phone::text").get(default="").strip()
            self.save_to_file("personal.json", result, is_json=True)

        yield result

    def save_to_file(self, filename, data, is_json=False):
        filepath = os.path.join(self.output_dir, filename)
        if is_json:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                if isinstance(data, list):
                    f.write("\n".join(str(item) for item in data))
                else:
                    f.write(str(data))

    def save_table(self, filename, table_data):
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", newline="", encoding="utf-8") as f:
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
        '1': 'title', '2': 'images', '3': 'links', '4': 'paragraphs', '5': 'spans',
        '6': 'pdfs', '7': 'docs', '8': 'videos', '9': 'audios', '10': 'tables',
        '11': 'quotes', '12': 'headings', '13': 'lists', '14': 'personal'
    }
    for key, value in options.items():
        print(f"{key}: {value.capitalize()}")
    selected_options = input("Enter Data Types to Scrap (comma separated, e.g., 1,3): ").split(",")
    data_types = [options[option.strip()] for option in selected_options if option.strip() in options]
    output_dir = "ScrapedData"
    run_spider(url, data_types, output_dir)

    # Zip the output directory
    with zipfile.ZipFile(f"{output_dir}.zip", "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(output_dir):
            for file in files:
                zf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_dir))

    print(f"Data scraped successfully and saved in {output_dir}.zip")