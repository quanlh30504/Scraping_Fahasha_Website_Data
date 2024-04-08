import scrapy
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


from ..items import FahasascrapingItem
from scrapy_selenium import SeleniumRequest

class FahasaspiderSpider(scrapy.Spider):
    name = "test"
    # custom_settings = {
    #     'FEEDS': {
    #         'bookData.json': {'format': 'json', 'overwrite': True}
    #     }
    # }

    page_num = 2
    page_foreign_num = 2

    def start_requests(self):
        url = 'https://www.fahasa.com/sach-trong-nuoc.html?order=num_orders&limit=24&p=1'
        yield SeleniumRequest(
            url=url,
            callback=self.parse,
            wait_time=10,
            wait_until=EC.element_to_be_clickable((By.CLASS_NAME, 'ma-box-content'))
        )

    def parse(self,response):

        books = response.css(".ma-box-content")
        for book in books:
            price = book.css(".price::text").get()
            if price is not None:
                url = book.css("a::attr(href)").get()
                yield response.follow(url, callback=self.parse_book_page)

        url_next_page = "https://www.fahasa.com/sach-trong-nuoc.html?order=num_orders&limit=24&p="+str(FahasaspiderSpider.page_num)
        if FahasaspiderSpider.page_num <= 1986:
            FahasaspiderSpider.page_num += 1
            yield response.follow(url_next_page,callback=self.parse)
        else:
            url_foreign_book = "https://www.fahasa.com/foreigncategory.html"
            yield response.follow(url_foreign_book, callback=self.parse_foreign_book)

    def parse_foreign_book(self, response):
        books = response.css(".ma-box-content")
        for book in books:
            price = book.css(".price::text").get()
            if price is not None:
                url = book.css("a::attr(href)").get()
                yield response.follow(url, callback=self.parse_book_page)

        url_next_page = "https://www.fahasa.com/foreigncategory.html?order=num_orders&limit=24&p=" + str(FahasaspiderSpider.page_foreign_num)
        if FahasaspiderSpider.page_foreign_num <= 527:
            FahasaspiderSpider.page_foreign_num += 1
            yield response.follow(url_next_page, callback=self.parse_foreign_book)


    def parse_book_page(self,response):
        items = FahasascrapingItem()

        items["Book_url"] = response.url
        title = response.css("h1::text").getall()
        items["Title"] = title[1].strip()
        items["Img_url"] = response.css("#image::attr(data-src)").get()
        items["Price"] = response.css(".price::text").get()
        if items["Price"] is not None:
            l = items["Price"].split()
            items["Price"] = l[0]

        Categories = response.css(".breadcrumb li>a::text").getall()
        for i in range(len(Categories)):
            if Categories[i] is not None:
                Categories[i].strip()
        items["Categories"] = Categories

        #detail book
        items["ISBN"] = response.css(".data_sku::text").get().strip()
        # items["SupplierName"] = response.css(".data_supplier::text").get()
        # if items["SupplierName"] is not None:
        #     items["SupplierName"] = items["SupplierName"].strip()

        items["Author"] = response.css(".data_author::text").get()
        if items["Author"] is not None:
            items["Author"] = items["Author"].strip()

        items["Publisher"] = response.css(".data_supplier a::text").get()
        if items["Publisher"] is not None:
            items["Publisher"] = items["Publisher"].strip()
        items["PublishYear"] = response.css(".data_publish_year::text").get()
        if items["PublishYear"] is not None:
            items["PublishYear"] = items["PublishYear"].strip()

        items["Language"] = response.css(".data_languages::text").get()
        if items["Language"] is not None :
            items["Language"] = items["Language"].strip()

        items["Weight_gr"] = response.css(".data_weight::text").get()
        if items["Weight_gr"] is not None :
            items["Weight_gr"] = items["Weight_gr"].strip()
        items["Size"] = response.css(".data_size::text").get()
        if items["Size"] is not None :
            items["Size"] = items["Size"].strip()
        items["NumOfPages"] = response.css(".data_qty_of_page::text").get()
        if items["NumOfPages"] is not None :
            items["NumOfPages"] = items["NumOfPages"].strip()
        items["LayoutBook"] = response.css(".data_book_layout::text").get()
        if items["LayoutBook"] is not None :
            items["LayoutBook"] = items["LayoutBook"].strip()


        title_desc =  response.css("#desc_content p strong::text").get()
        description = ""
        if title_desc is not None:
            description = title_desc + "\n"
        Descrpitions = response.css("#desc_content p::text").getall()
        for desc in Descrpitions:
            description += desc
            description += "\n"
        items["Description"] = description

        yield items
        pass
