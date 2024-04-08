# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FahasascrapingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()

    Book_url = scrapy.Field()
    Title = scrapy.Field()
    Img_url = scrapy.Field()
    Price = scrapy.Field()
    Categories = scrapy.Field()

    # detail book
    ISBN = scrapy.Field()
    SupplierName = scrapy.Field()
    Author = scrapy.Field()
    Publisher = scrapy.Field()
    PublishYear = scrapy.Field()
    Language = scrapy.Field()
    Weight_gr = scrapy.Field()
    Size = scrapy.Field()
    NumOfPages = scrapy.Field()
    LayoutBook = scrapy.Field()
    Description = scrapy.Field()
    pass
