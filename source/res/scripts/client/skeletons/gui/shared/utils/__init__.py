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

    def getItemsEx(self, itemTypeIDs, criteria=None, nationID=None):
        raise NotImplementedError

    def getVehicles(self, criteria=None):
        raise NotImplementedError

    def getBadges(self, criteria=None):
        raise NotImplementedError

    def getItemByCD(self, typeCompDescr):
        """
        Trying to return item from inventory by item int
        compact descriptor, otherwise - from shop.
        
        @param typeCompDescr: item int compact descriptor
        @return: item object
        """
        raise NotImplementedError

    def getItem(self, itemTypeID, nationID, innationID):
        """
        Returns item from inventory by given criteria or
        from shop.
        
        @param itemTypeID: item type index from common.items.ITEM_TYPE_NAMES
        @param nationID: nation index from nations.NAMES
        @param innationID: item index within its nation
        @return: gui item
        """
        raise NotImplementedError

    def getTankmanDossier(self, tmanInvID):
        """
        Returns tankman dossier item by given tankman
        inventory id
        
        @param tmanInvID: tankman inventory id
        @return: TankmanDossier object
        """
        raise NotImplementedError

    def getVehicleDossier(self, vehTypeCompDescr, databaseID=None):
        """
        Returns vehicle dossier item by given vehicle type
        int compact descriptor
        
        @param vehTypeCompDescr: vehicle type in compact descriptor
        @return: VehicleDossier object
        """
        raise NotImplementedError

    def getVehicleDossiersIterator(self):
        raise NotImplementedError

    def getAccountDossier(self, databaseID=None):
        """
        Returns account dossier item
        @return: AccountDossier object
        """
        raise NotImplementedError

    def getClanInfo(self, databaseID=None):
        raise NotImplementedError

    def getPreviousItem(self, itemTypeID, invDataIdx):
        raise NotImplementedError

    def doesVehicleExist(self, intCD):
        """ returns existing flag of target vehicle's int compact descriptor.
        Raises error in case of given non-vehicle CD.
        """
        raise NotImplementedError
