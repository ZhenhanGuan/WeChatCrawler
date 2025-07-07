import pymongo

class MongoPipeline:
    def open_spider(self, spider):
        self.client = pymongo.MongoClient('mongodb://localhost:27017/')
        self.db = self.client['website_crawler_db']
        self.collection = self.db['pages']

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item
