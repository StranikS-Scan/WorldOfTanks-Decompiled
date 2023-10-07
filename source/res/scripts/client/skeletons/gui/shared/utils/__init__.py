# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/shared/utils/__init__.py
from typing import TYPE_CHECKING, Optional
from skeletons.gui.shared.utils import requesters
if TYPE_CHECKING:
    from gui.shared.gui_items import ItemsCollection
    from gui.shared.gui_items.Tankman import Tankman
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.veh_post_progression.models.progression import PostProgressionItem
    from items.vehicles import VehicleType
    from gui.shared.gui_items.dossier import AccountDossier

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
    def vehicleRotation(self):
        raise NotImplementedError

    @property
    def ranked(self):
        raise NotImplementedError

    @property
    def battleRoyale(self):
        raise NotImplementedError

    @property
    def badges(self):
        raise NotImplementedError

    @property
    def epicMetaGame(self):
        raise NotImplementedError

    @property
    def blueprints(self):
        raise NotImplementedError

    @property
    def tokens(self):
        raise NotImplementedError

    @property
    def sessionStats(self):
        raise NotImplementedError

    @property
    def anonymizer(self):
        raise NotImplementedError

    @property
    def battlePass(self):
        raise NotImplementedError

    @property
    def giftSystem(self):
        raise NotImplementedError

    @property
    def gameRestrictions(self):
        raise NotImplementedError

    @property
    def resourceWell(self):
        raise NotImplementedError

    @property
    def achievements20(self):
        raise NotImplementedError

    @property
    def refProgram(self):
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

    def getStockVehicle(self, typeCompDescr):
        raise NotImplementedError

    def getVehicleCopy(self, vehicle):
        raise NotImplementedError

    def getVehicleCopyByCD(self, typeCompDescr):
        raise NotImplementedError

    def getLayoutsVehicleCopy(self, vehicle, ignoreDisabledProgression=False):
        raise NotImplementedError

    def getTankman(self, tmanInvID):
        raise NotImplementedError

    def getCrewSkin(self, skinID):
        raise NotImplementedError

    def getTankmen(self, criteria=None):
        raise NotImplementedError

    def getInventoryTankmen(self, criteria=None):
        raise NotImplementedError

    def getDismissedTankmen(self, criteria=None):
        raise NotImplementedError

    def removeUnsuitableTankmen(self, tankmen, criteria=None):
        raise NotImplementedError

    def tankmenInBarracksCount(self):
        raise NotImplementedError

    def freeTankmenBerthsCount(self):
        raise NotImplementedError

    def getItems(self, itemTypeID=None, criteria=None, nationID=None, onlyWithPrices=True):
        raise NotImplementedError

    def getItemsAsync(self, itemTypeID=None, criteria=None, nationID=None, onlyWithPrices=True, callback=None):
        raise NotImplementedError

    def getVehicles(self, criteria=None):
        raise NotImplementedError

    def getStyles(self, criteria=None):
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

    def getDogTag(self, databaseID=None):
        raise NotImplementedError

    def getBattleRoyaleStats(self, arenaType, databaseID=None, vehicleIntCD=None):
        raise NotImplementedError

    def getVehPostProgression(self, vehIntCD, vehType=None):
        raise NotImplementedError

    def getPreviousItem(self, itemTypeID, invDataIdx):
        raise NotImplementedError

    def doesVehicleExist(self, intCD):
        raise NotImplementedError

    def onDisconnected(self):
        raise NotImplementedError

    def getWTR(self, databaseID=None):
        raise NotImplementedError

    def getLayout(self, databaseID=None):
        raise NotImplementedError

    def getLayoutState(self, databaseID=None):
        raise NotImplementedError


class IHangarSpace(object):
    onStatsReceived = None
    onSpaceCreating = None
    onSpaceCreate = None
    onSpaceDestroy = None
    onMouseEnter = None
    onMouseExit = None
    onMouseDown = None
    onMouseUp = None
    onVehicleChangeStarted = None
    onVehicleChanged = None
    onSpaceRefresh = None
    onSpaceRefreshCompleted = None
    onHeroTankReady = None
    onSpaceChanged = None
    onNotifyCursorOver3dScene = None
    onSpaceChangedByAction = None

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
    def isSelectionEnabled(self):
        raise NotImplementedError

    @property
    def isCursorOver3DScene(self):
        raise NotImplementedError

    @property
    def spacePath(self):
        raise NotImplementedError

    @property
    def visibilityMask(self):
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

    def startToUpdateVehicle(self, vehicle, outfit=None):
        raise NotImplementedError

    def updateVehicleDescriptor(self, descr):
        raise NotImplementedError

    def updatePreviewVehicle(self, vehicle, outfit=None):
        raise NotImplementedError

    def removeVehicle(self):
        raise NotImplementedError

    def onPremiumChanged(self, isPremium, attrs, premiumExpiryTime):
        raise NotImplementedError

    def setVehicleSelectable(self, flag):
        raise NotImplementedError

    def updateVehicleOutfit(self, outfit):
        raise NotImplementedError

    def getVehicleEntity(self):
        raise NotImplementedError

    def getVehicleEntityAppearance(self):
        raise NotImplementedError

    def getCentralPointForArea(self, areaID):
        raise NotImplementedError

    def setSelectionEnabled(self, enabled):
        raise NotImplementedError

    def getAnchorParams(self, slotId, areaId, regionId):
        raise NotImplementedError

    def updateAnchorsParams(self, *args):
        raise NotImplementedError


class IHangarSpaceReloader(object):

    def init(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def changeHangarSpace(self, spaceName, visibilityMask, waitingMessage=None, backgroundImage=None):
        raise NotImplementedError

    @property
    def hangarSpacePath(self):
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

    def getAchievementImageUrl(self, imgType, achieveID):
        raise NotImplementedError
