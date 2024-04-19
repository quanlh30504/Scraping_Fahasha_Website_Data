# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter

import pymysql
import pymongo
import random


class FahasascrapingPipeline:
    def process_item(self, item, spider):
        return item


class SavingToMongoDbPipeline:
    def __init__(self):
        myclient = pymongo.MongoClient("mongodb://localhost:27017")
        mydb = myclient["DataCrawl"]
        self.mycol = mydb["FahasaBook"]

    def process_item(self, item, spider):
        self.mycol.insert_one(dict(item))
        return item


class SavingToMySqlPipeline:
    def __init__(self):
        self.create_connection()

    def create_connection(self):
        self.mydb = pymysql.connect(
            host="localhost",
            user="root",
            password="quannguyen2004",
            database="better_read"
        )

        self.cur = self.mydb.cursor()

    def process_item(self, item, spider):

        self.cur.execute("SET FOREIGN_KEY_CHECKS = 0")

        # insert data to publisher table
        publisher_name = item["Publisher"]  # possible NUll
        self.publisher_id = self.insert_publisher(publisher_name)

        # insert data to book table
        book_id = self.insert_book(item)

        # insert author
        author_name = item["Author"]
        self.insert_author(book_id, author_name)

        # insert category
        categories = item["Categories"]
        self.insert_category(book_id, categories)

        # insert inventory
        self.insert_iventory(book_id)

        #insert promotion
        self.insert_promotion(book_id)

        self.cur.execute("SET FOREIGN_KEY_CHECKS = 1")

        self.mydb.commit()

        return item

    def insert_book(self, item):
        title = item["Title"]
        isbn = item["ISBN"]
        price = float(item["Price"])
        image_url = item["Img_url"]
        weight_gr = item["Weight_gr"]
        size = item["Size"]
        layout = item["LayoutBook"]
        publication_date = item["PublishYear"]
        if publication_date is not None:
            if len(publication_date) <= 4:
                year = item["PublishYear"]
                month = random.randint(1, 12)
                day = random.randint(1, 28)
                f = "{}-{}-{}"
                publication_date = f.format(year, month, day)
            else:
                publication_date = "2023-1-1"
        language = item["Language"]  ## possible NULL
        pages = item["NumOfPages"]
        if pages is not None:
            pages = int(pages)
        description = item["Description"]

        values = (
        title, isbn, self.publisher_id, publication_date, language, pages, description, price, image_url, weight_gr,
        size, layout,)
        self.cur.execute(
            "insert into book(title,isbn,publisher_id,publication_date,language,pages,description,price,image_url,weight_gr,size,layout_book) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            values)
        book_id = self.cur.lastrowid
        # self.mydb.commit()
        return book_id

    ## Chú ý bug : sẽ có 1 vài publisher , language, ... bị null

    def insert_publisher(self, publisher_name):
        publisher_id = None
        if publisher_name is not None:
            self.cur.execute("select id from publisher where name = %s", (publisher_name,))
            result = self.cur.fetchone()
            if result:
                publisher_id = result[0]
            else:
                self.cur.execute("insert into publisher (name) values(%s)", (publisher_name,))
                publisher_id = self.cur.lastrowid

        # self.mydb.commit()
        return publisher_id

    def insert_iventory(self, book_id):
        quantity = random.randint(100, 500)
        self.cur.execute("insert into inventory (book_id,quantity) values(%s,%s)",(book_id, quantity,))
        # self.mydb.commit()

    def insert_author(self, book_id, author_name):
        # author and book_author
        author_id = None
        if author_name is not None:
            self.cur.execute("select id from author where name = %s", (author_name,))
            result = self.cur.fetchone()
            if result:
                author_id = result[0]
            else:
                self.cur.execute("insert into author (name) values(%s)", (author_name,))
                author_id = self.cur.lastrowid

        self.cur.execute("insert into book_author (book_id, author_id) values(%s,%s)", (book_id, author_id,))

        # self.mydb.commit()

    def insert_category(self, book_id, categories):
        self.cur.execute("select id from category where name = %s", (categories[0],))
        result = self.cur.fetchone()
        category_id = result
        # thêm mục catagory mẹ vào category table vs book_category
        parent_id = None
        if result is not None:
            parent_id = result[0]
        else:
            self.cur.execute("insert into category (name,parent_id) values(%s,%s)", (categories[0], parent_id,))
            category_id = self.cur.lastrowid
            parent_id = category_id


        for i in range(1, len(categories)):
            self.cur.execute("select id from category where name = %s", (categories[i],))
            result = self.cur.fetchone()
            if result:
                parent_id = result[0]
            else:
                self.cur.execute("insert into category(name,parent_id) values(%s,%s)", (categories[i], parent_id,))
                parent_id = self.cur.lastrowid
            if i == len(categories) - 1:
                category_id = parent_id

        self.cur.execute("insert into book_category (book_id,category_id) values(%s,%s)",
                         (book_id, category_id,))

        # self.mydb.commit()


    def insert_promotion(self,book_id):
        # promotion_id = random.randint(1,10)
        self.cur.execute("insert into book_promotion(book_id,promotion_id) values(%s,%s)",(book_id,3,))
