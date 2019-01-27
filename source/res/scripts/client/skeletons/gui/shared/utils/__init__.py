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

    @property
    def epicMetaGame(self):
        raise NotImplementedError

    @property
    def tokens(self):
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

    def getItems(self, itemTypeID=None, criteria=None, nationID=None, onlyWithPrices=True):
        raise NotImplementedError

    def getVehicles(self, criteria=None):
        raise NotImplementedError

    def getBadges(self, criteria=None):
        raise NotImplementedError

    def getBadgeByID(self, badgeID):
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


class IHangarSpace(object):
    onStatsReceived = None
    onSpaceCreate = None
    onSpaceDestroy = None
    onMouseEnter = None
    onMouseExit = None
    onMouseDown = None
    onMouseUp = None
    onVehicleChangeStarted = None
    onVehicleChanged = None
    onSpaceRefresh = None
    onHeroTankReady = None
    onSpaceChanged = None

    @property
    def space(self):
        raise NotImplementedError

    @property
    def inited(self):
        raise NotImplementedError

    @property
    def spaceInited(self):
        raise NotImplementedError

    @property
    def isPremium(self):
        raise NotImplementedError

    @property
    def isModelLoaded(self):
        raise NotImplementedError

    @property
    def isCursorOver3DScene(self):
        raise NotImplementedError

    def spaceLoading(self):
        raise NotImplementedError

    def init(self, isPremium):
        raise NotImplementedError

    def refreshSpace(self, isPremium, forceRefresh=False):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def updateVehicle(self, vehicle):
        raise NotImplementedError

    def startToUpdateVehicle(self, vehicle):
        raise NotImplementedError

    def updatePreviewVehicle(self, vehicle):
        raise NotImplementedError

    def removeVehicle(self):
        raise NotImplementedError

    def onPremiumChanged(self, isPremium, attrs, premiumExpiryTime):
        raise NotImplementedError

    def leftButtonClicked(self):
        raise NotImplementedError

    def setVehicleSelectable(self, flag):
        raise NotImplementedError

    def updateVehicleOutfit(self, outfit):
        raise NotImplementedError

    def getVehicleEntity(self):
        raise NotImplementedError

    def getCentralPointForArea(self, areaID):
        raise NotImplementedError


class IRaresCache(object):
    onTextReceived = None
    onImageReceived = None

    def request(self, listOfIds):
        raise NotImplementedError

    def isLocallyLoaded(self, achieveID):
        raise NotImplementedError

    def getTitle(self, achieveID):
        raise NotImplementedError

    def getDescription(self, achieveID):
        raise NotImplementedError

    def getImageData(self, imgType, achieveID):
        raise NotImplementedError

    def getHeroInfo(self, achieveID):
        raise NotImplementedError

    def getConditions(self, achieveID):
        raise NotImplementedError
