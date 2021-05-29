# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/vehicle_appearance_cache.py


class IAppearanceCache(object):

    def getAppearance(self, vId, vInfo, callback=None):
        raise NotImplementedError

    def removeAppearance(self, vId):
        raise NotImplementedError

    def stopLoading(self, vId):
        raise NotImplementedError

    def loadResources(self, compactDescr, prereqs):
        raise NotImplementedError

    def unloadResources(self, compactDescr):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError
