# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/shared/utils/__init__.py
from skeletons.gui.shared.utils import requesters

class IItemsRequester(requesters.IRequester):

    @property
    def inventory(self):
        raise NotImplementedError

    @property
    def stats(self):
        raise NotImplementedError

    @property
    def dossiers(self):
        raise NotImplementedError

    @property
    def goodies(self):
        raise NotImplementedError

    @property
    def shop(self):
        raise NotImplementedError

    @property
    def recycleBin(self):
        raise NotImplementedError

    @property
    def ranked(self):
        raise NotImplementedError

    @property
    def badges(self):
        raise NotImplementedError

    def requestUserDossier(self, databaseID, callback):
        raise NotImplementedError

    def unloadUserDossier(self, databaseID):
        raise NotImplementedError

    def requestUserVehicleDossier(self, databaseID, vehTypeCompDescr, callback):
        raise NotImplementedError

    def invalidateCache(self, diff=None):
        raise NotImplementedError

    def getVehicle(self, vehInvID):
        raise NotImplementedError

    def getStockVehicle(self, typeCompDescr, useInventory=False):
        raise NotImplementedError

    def getVehicleCopy(self, vehicle):
        raise NotImplementedError

    def getTankman(self, tmanInvID):
        raise NotImplementedError

    def getTankmen(self, criteria=None):
        raise NotImplementedError

    def getItems(self, itemTypeID=None, criteria=None, nationID=None):
        raise NotImplementedError

    def getVehicles(self, criteria=None):
        raise NotImplementedError

    def getBadges(self, criteria=None):
        raise NotImplementedError

    def getItemByCD(self, typeCompDescr):
        raise NotImplementedError

    def getItem(self, itemTypeID, nationID, innationID):
        raise NotImplementedError

    def getTankmanDossier(self, tmanInvID):
        raise NotImplementedError

    def getVehicleDossier(self, vehTypeCompDescr, databaseID=None):
        raise NotImplementedError

    def getVehicleDossiersIterator(self):
        raise NotImplementedError

    def getAccountDossier(self, databaseID=None):
        raise NotImplementedError

    def getClanInfo(self, databaseID=None):
        raise NotImplementedError

    def getPreviousItem(self, itemTypeID, invDataIdx):
        raise NotImplementedError

    def doesVehicleExist(self, intCD):
        raise NotImplementedError
