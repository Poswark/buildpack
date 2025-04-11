from pymongo import MongoClient
import os

MONGO_HOST = os.getenv("MONGO_HOST")
MONGO_PORT = os.getenv("MONGO_PORT")
MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASS = os.getenv("MONGO_PASS")

MONGODB_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/?authSource=admin&readPreference=primary&ssl=false&directConnection=true"

client = MongoClient(MONGODB_URI)
database = client["finanzas"]

expenses_collection = database["expenses"]
month_collection = database["month"]
users_collection = database["users"]
reports_collection = database["reports"]
