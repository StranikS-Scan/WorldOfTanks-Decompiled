# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/entitlements.py


class EntitlementsData(object):

    def __init__(self):
        self.__validEntitlements = set()
        self.__validationQueue = set()

    def getValidEntitlements(self):
        return self.__validEntitlements

    def addValidEntitlementsToCache(self, entitlementIDsList):
        self.__validEntitlements.update(entitlementIDsList)

    def isEntitlementValid(self, entitlementID):
        return entitlementID in self.__validEntitlements

    def addEntitlementToValidationQueue(self, entitlementID):
        self.__validationQueue.add(entitlementID)

    def getValidationQueue(self):
        return list(self.__validationQueue)


g_entitlementsData = EntitlementsData()
