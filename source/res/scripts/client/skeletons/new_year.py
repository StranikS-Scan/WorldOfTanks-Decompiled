# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/new_year.py
import typing
from adisp import async
from items.components.ny_constants import RANDOM_VALUE
from skeletons.gui.game_control import IFestivityController, IGameController
if typing.TYPE_CHECKING:
    from Event import Event
    from gui.server_events.event_items import CelebrityGroup, TokenQuest, CelebrityQuest, CelebrityTokenQuest
    from items.components.ny_constants import FillerState, TOY_SLOT_USAGE
    from Math import Vector3
    from NewYearCelebrityObject import NewYearCelebrityObject
    from NewYearCelebrityEntryObject import NewYearCelebrityEntryObject

class ICustomizableObjectsManager(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    @property
    def pendingEntitiesToDestroy(self):
        raise NotImplementedError

    def addCustomizableEntity(self, entity):
        raise NotImplementedError

    def removeCustomizableEntity(self, entity):
        raise NotImplementedError

    def getCustomizableEntity(self, anchorName):
        raise NotImplementedError

    def addCameraAnchor(self, anchorName, anchor):
        raise NotImplementedError

    def removeCameraAnchor(self, anchorName):
        raise NotImplementedError

    def getCameraAnchor(self, anchorName):
        raise NotImplementedError

    def getCurrentCameraAnchor(self):
        raise NotImplementedError

    def addCameraTarget(self, anchorName, cameraTarget):
        raise NotImplementedError

    def removeCameraTarget(self, anchorName):
        raise NotImplementedError

    def getCameraTarget(self, anchorName):
        raise NotImplementedError

    def updateSlot(self, slot, toy, withHangingEffect=True):
        raise NotImplementedError

    def switchCamera(self, anchorName, instantly=False):
        raise NotImplementedError

    def getEffect(self, effectName):
        raise NotImplementedError

    def setSlotHighlight(self, slot, isEnabled):
        raise NotImplementedError


class INewYearController(IFestivityController):
    onDataUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    def isPostEvent(self):
        raise NotImplementedError

    def isFinished(self):
        raise NotImplementedError

    def isSuspended(self):
        raise NotImplementedError

    def isMaxAtmosphereLevel(self):
        raise NotImplementedError

    def isVehicleBranchEnabled(self):
        raise NotImplementedError

    def getHangarQuestsFlagData(self):
        raise NotImplementedError

    def getHangarWidgetLinkage(self):
        raise NotImplementedError

    def getHangarEdgeColor(self):
        raise NotImplementedError

    def getSlotDescrs(self, objectName=None):
        raise NotImplementedError

    def getPureSlotForToy(self, toy):
        raise NotImplementedError

    def hasPureSlotForToy(self, toy):
        raise NotImplementedError

    def getToyDescr(self, toyID):
        raise NotImplementedError

    def getToysByType(self, slotID):
        raise NotImplementedError

    def getAllCollectedToysId(self):
        raise NotImplementedError

    @async
    def hangToy(self, toyID, slotID, toyUsage=None, callback=None):
        raise NotImplementedError

    def getLevel(self, level):
        raise NotImplementedError

    def checkForNewToys(self, slot=None, objectType=None):
        raise NotImplementedError

    def getToysInSlots(self, objectName=None):
        raise NotImplementedError

    def isCollectionCompleted(self, collectionID=None):
        raise NotImplementedError

    def getFinishTime(self):
        raise NotImplementedError

    def showStateMessage(self):
        raise NotImplementedError

    def sendSeenToys(self, toyIDs):
        raise NotImplementedError

    def sendSeenToysInCollection(self, toyIDs):
        raise NotImplementedError

    def sendViewAlbum(self, settingID, rank):
        raise NotImplementedError

    def isLastDayOfEvent(self):
        raise NotImplementedError

    def getVehicleBranch(self):
        raise NotImplementedError

    def getUniqueMegaToysCount(self):
        raise NotImplementedError

    def isFullRegularToysGroup(self, typeID, settingID, rank):
        raise NotImplementedError

    def isRegularToysCollected(self):
        raise NotImplementedError

    def getMaxToysStyle(self):
        raise NotImplementedError

    def getActiveSettingBonusValue(self):
        raise NotImplementedError

    def getActiveMultiplier(self):
        raise NotImplementedError

    def getActiveMegaToysBonus(self):
        raise NotImplementedError

    def getActiveCollectionsBonus(self):
        raise NotImplementedError

    def isOldCollectionBubbleNeeded(self, years):
        raise NotImplementedError

    def isOldRewardsBubbleNeeded(self, years):
        raise NotImplementedError

    def markPreviousYearTabVisited(self, yearName, uiFlagKey):
        raise NotImplementedError

    def prepareNotifications(self, tokens):
        raise NotImplementedError


class IJukeboxController(IGameController):
    onPlaylistSelected = None
    onTrackSuspended = None
    onHighlightEnable = None
    onHighlighted = None
    onFaded = None

    def onAnimatorEvent(self, name):
        raise NotImplementedError

    def handleJukeboxClick(self, side):
        raise NotImplementedError

    def handleJukeboxHighlight(self, side, isHighlighed):
        raise NotImplementedError

    def setJukeboxPosition(self, position):
        raise NotImplementedError


class ICelebritySceneController(IGameController):
    onQuestsUpdated = None

    @property
    def isChallengeVisited(self):
        raise NotImplementedError

    @property
    def isWelcomeAnimationViewed(self):
        raise NotImplementedError

    @property
    def isInChallengeView(self):
        raise NotImplementedError

    @property
    def isChallengeCompleted(self):
        raise NotImplementedError

    @property
    def hasNewCompletedQuests(self):
        raise NotImplementedError

    @property
    def questGroups(self):
        raise NotImplementedError

    @property
    def quests(self):
        raise NotImplementedError

    @property
    def tokens(self):
        raise NotImplementedError

    @property
    def marathonQuests(self):
        raise NotImplementedError

    @property
    def completedQuestsMask(self):
        raise NotImplementedError

    @property
    def questsCount(self):
        raise NotImplementedError

    @property
    def completedQuestsCount(self):
        raise NotImplementedError

    def addCelebrityEntity(self, entity):
        raise NotImplementedError

    def removeCelebrityEntity(self):
        raise NotImplementedError

    def addCelebrityEntryEntity(self, entity):
        raise NotImplementedError

    def removeCelebrityEntryEntity(self):
        raise NotImplementedError

    def onEnterChallenge(self):
        raise NotImplementedError

    def onExitChallenge(self):
        raise NotImplementedError

    def onSimplifyQuest(self):
        raise NotImplementedError

    def onAnimatorEvent(self, name):
        raise NotImplementedError


class INewYearCraftMachineController(IGameController):
    isMegaDeviceTurnedOn = False
    selectedToyTypeIdx = RANDOM_VALUE
    selectedToySettingIdx = 0
    selectedToyRankIdx = 0
    fillerState = None

    @property
    def fillerShardsCost(self):
        raise NotImplementedError

    @property
    def isConnected(self):
        raise NotImplementedError

    def getSelectedToyType(self):
        raise NotImplementedError

    def getToyCategoryType(self):
        raise NotImplementedError

    def getRegularSelectedToyType(self):
        raise NotImplementedError

    def setSettings(self, toyTypeID=RANDOM_VALUE, settingID=RANDOM_VALUE, rank=RANDOM_VALUE, isMegaOn=False):
        raise NotImplementedError

    def calculateSelectedToyCraftCost(self):
        raise NotImplementedError

    def calculateToyCraftCost(self, isMegaToy, toyTypeIdx, toySettingIdx, toyRankIdx, fillerState):
        raise NotImplementedError

    def calculateMegaToyCraftCost(self):
        raise NotImplementedError

    def getActualMegaDeviceState(self):
        raise NotImplementedError

    def getDesiredMegaDeviceState(self, isMegaDeviceTurnedOn):
        raise NotImplementedError
