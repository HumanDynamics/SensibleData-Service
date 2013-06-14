import pymongo
import service_config
import log_config
from utils import log_config as CONFIG
from loggerApp import helperModule

class LogDatabase(object):

	client = None
	db = None
	collection = None

        def __init__(self):
                self.client = pymongo.MongoClient(log_config.LOGGER_DATABASE['params']['url']%(log_config.LOGGER_DATABASE['params']['username'],log_config.LOGGER_DATABASE['params']['password']))
		self.db = self.client[log_config.LOGGER_DATABASE['params']['database']]
		self.collection = self.db[log_config.LOGGER_DATABASE['params']['collection']]


	def insert(self, document):
		return self.collection.insert(document)

	def getDocuments(self, query, collection):
		return self.db[collection].find(query)

        def writeEntry(self, flowID, D, C, Y):
                returned = self.collection.insert({"flowID" : flowID, "D": D, "C" : C , "Y" : Y})
                return str(returned)

        def writeEntryWithMAC(self, flowID, D, C, Y, A):
                returned = self.collection.insert({"flowID" : flowID, "D": D, "C" : C , "Y" : Y, "A" : A})
                return str(returned)

        def writeEntryWith_Z(self, flowID, D, V, Z):
            returned = self.collection.insert({"flowID" : flowID, "D": D, "V" : V , "Z" : Z})
            return str(returned)


        def getMaxFlowID(self):
            maxFlowID = 0
            resultEntry = self.collection.find_one(sort=[("flowID", -1)])
            if (resultEntry is not None):
                    maxFlowID = resultEntry['flowID']
#		print "maxFLowID = " + str(maxFlowID)
            return maxFlowID


# TODO:
        def getMaxUserAppFlow(self, userID, appID):
            return self.collection.find().sort("userAppFlow", pymongo.DESCENDING).count()

        
        def getPrevious(self, flowID):
            previous = flowID - 1
            result = self.collection.find_one({"flowID" : previous})
            return result

        def getEntry(self, flowID):
#		print "flowID = " + str(flowID)
            result = self.collection.find_one({"flowID" : flowID})
            return result

        def getAuthenticationKey(self, flowID):
            result = self.collection.find({"flowID" : flowID})
            # Some sanity checks and early returns
            if (result is None or result.count() == 0):
                    print "flowID = " + str(flowID) + " not found"
                    return -1
            elif (result.count() > 1):
                    print "More than ONE authentication key A for flowID = " + str(flowID)
                    return -2
            elif (result.count() == 1):
                    return self.collection.find_one({"flowID" : flowID}).get("A") # Retrieve the Authentication key used for that event

        def getLastEntry(self, userID):
#               return self.collection.find({"D.userID" : userID}, sort=[("D.userAppFlow", pymongo.DESCENDING)]).limit(1)
            return self.collection.find_one({"D.userID" : userID}, sort=[("D.userAppFlow", pymongo.DESCENDING)])

        def count(self, userID):
            return self.collection.find({"D.userID" : userID}).count()

        def getAllFlowIDs(self, userID):
            return self.collection.find({"D.userID" : userID}, {"flowID" : 1, "_id" : 0}, sort=[("flowID", pymongo.DESCENDING)])

        def getPublicSeed(self):
            return CONFIG.Y0

        def getZ0(self):
            return CONFIG.Z0

# TODO: if there are NO entries, it crashes.
        def getLastY(self):
            maxFlowID = self.getMaxFlowID()
            lastEntry = self.getEntry(maxFlowID)
            toReturn = lastEntry.get("Y")
            return toReturn

        def getLast_Z(self):
            maxFlowID = self.getMaxFlowID()
            lastEntry = self.getEntry(maxFlowID)
            toReturn = lastEntry.get("Z")
            return toReturn

        def reset(self):
            self.collection.remove()
