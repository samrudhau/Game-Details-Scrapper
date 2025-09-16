# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import sqlite3
import json

class GamesSpiderPipeline:
    def __init__(self):
        self.create_connection()
        self.create_table()

    def create_connection(self):
        self.conn = sqlite3.connect("games.db")
        self.curr = self.conn.cursor()

    def create_table(self):
        # This drops the old table each time the spider is run.
        # This is good for testing and demos.
        self.curr.execute("DROP TABLE IF EXISTS games_tb")
        self.curr.execute("""
            CREATE TABLE games_tb (
                title TEXT,
                description TEXT,
                category TEXT,
                price TEXT,
                developer TEXT,
                platform TEXT,
                game_type TEXT,
                image TEXT,
                availability TEXT
            )
        """)

    def process_item(self, item, spider):
        self.store_db(item, spider)
        return item

    def store_db(self, item, spider):
        self.curr.execute("""
            INSERT INTO games_tb (title, description, category, price, developer, platform, game_type, image, availability)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item['title'], 
            item['description'], 
            json.dumps(item['category']),
            item['price'],
            item['developer'],
            item['platform'],
            item['game_type'],
            item['image'],
            item['availability']

        ))
        self.conn.commit()
        spider.logger.info(f"Inserted: {item['title']}")

