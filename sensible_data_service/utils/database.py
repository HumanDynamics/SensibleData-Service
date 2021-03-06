from pymongo import MongoClient
import SECURE_settings
from django.conf import settings

class Database:
	client = None
	db = None

	def __init__(self):
		self.client = MongoClient(settings.DATA_DATABASE['params']['url']%(SECURE_settings.DATA_DATABASE['username'],SECURE_settings.DATA_DATABASE['password']))
		self.db = self.client[settings.DATA_DATABASE['params']['database']]

	def insert(self, documents, collection):
		coll = self.db[collection]
		doc_id = coll.insert(documents, continue_on_error=True)
		return doc_id

	def getDocuments(self, query, collection):
		coll = self.db[collection]
		return coll.find(query)
