from pymongo import MongoClient
from pymongo import cursor
from Stock import Stock
from flask_login import UserMixin
import re
import os


class User(UserMixin):
    def __init__(self, name):
        self.name = name
    def get_id(self):
        return self.name
    @staticmethod
    def users_collection():
        myclient = MongoClient(f"mongodb+srv://{os.getenv('DB_NAME')}:{os.getenv('PASS')}@cluster0-twyu7.mongodb.net/test?retryWrites=true&w=majority")
        db = myclient["users_stats"]
        users_collection = db["users_collection"]
        return users_collection
    def stats_database(self):
        myclient = MongoClient(f"mongodb+srv://{os.getenv('DB_NAME')}:{os.getenv('PASS')}@cluster0-twyu7.mongodb.net/test?retryWrites=true&w=majority")
        db = myclient["users_stats"]
        user_stats = db[self.name]
        return user_stats

    def buy(self, company_name, quantity):
        if (quantity):
            quantity = int(quantity)
        else:
            quantity = 1
        stock_list = Stock.stock_list()
        user_stats = self.stats_database()
        users_collection = self.users_collection()
        cursor=users_collection.find_one({"user_name": self.name})
        current_balance = float(cursor.get("balance"))
        cost = quantity * float(stock_list.get(company_name))
        if current_balance < cost:
            return False
        current_balance = current_balance - cost
        users_collection.update_one({"user_name": self.name}, {"$set": {"balance": current_balance}})
        current_quantity = 0
        for cursor in user_stats.find({}):
            if company_name in cursor:
                current_quantity = cursor[company_name]
                break
        user_stats.update_one({company_name: current_quantity},
                              {"$set": {company_name: current_quantity + quantity}}, upsert=True)

        return True

    def get_balance(self):
        users_collection = self.users_collection()
        cursor=users_collection.find_one({"user_name": self.name})
        return cursor.get("balance")

    def sell(self, company_name, quantity):
        if quantity:
            quantity = int(quantity)
        else:
            quantity = 1

        stock_list = Stock.stock_list()
        user_stats = self.stats_database()
        for cursor in user_stats.find({}):
            if company_name in cursor:
                current_quantity = cursor[company_name]
                break
        if current_quantity < quantity:
            return False
        if current_quantity - quantity == 0:
            user_stats.delete_one({company_name: current_quantity})
        else:
            user_stats.update({company_name: current_quantity}, {company_name: current_quantity - quantity})

        users_collection = self.users_collection()
        cursor = users_collection.find_one({"user_name": self.name})
        current_balance = cursor.get("balance")

        prise = quantity * float(stock_list.get(company_name))
        current_balance = current_balance + prise
        users_collection.update_one({"user_name": self.name}, {"$set": {"balance": current_balance}})
        return True

    def get_stats(self):
        user_stats = self.stats_database()
        stats = {}
        for stat in user_stats.find({}):
            x = re.split(':|\,', (str(stat)))
            company_name = (x[2][2:-1])
            quantity = (x[3][1:-1])
            stats[company_name] = quantity
        return stats

    def get_share_value(self):
        stock_list = Stock.stock_list()
        stats = self.get_stats()
        return sum((float(stock_list.get(k, 0)) * int(v)) for k, v in zip(stats, stats.values()))


