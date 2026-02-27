from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")

db = client["secure_ai_platform"]

admins = db["admins"]

students = db["students"]

files = db["files"]