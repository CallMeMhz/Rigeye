from pymongo import MongoClient
from bson import ObjectId


def connect_mongodb(app):
    client = MongoClient(host=app.config['DATABASE_URL'], port=app.config['DATABASE_PORT'])
    return client
