# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/new_year.py
import typing
from adisp import async
from skeletons.gui.game_control import IFestivityController, IGameController
if typing.TYPE_CHECKING:
    from Event import Event
    from NewYearCelebrityObject import NewYearCelebrityObject
    from NewYearCelebrityEntryObject import NewYearCelebrityEntryObject
    from NewYearTalismanObject import NewYearTalismanObject
    from NewYearTalismanPreviewObject import NewYearTalismanPreviewObject
    from gui.server_events.event_items import CelebrityGroup, TokenQuest, CelebrityQuest, CelebrityTokenQuest
    from NewYearIcicleObject import NewYearIcicleObject
    from NewYearIciclesIllumination import NewYearIciclesIllumination

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

    def addCameraTarget(self, anchorName, cameraTarget):
        raise NotImplementedError

    def removeCameraTarget(self, anchorName):
        raise NotImplementedError

    def getCameraTarget(self, anchorName):
        raise NotImplementedError

    def updateSlot(self, slot, toy, withHangingEffect=True):
        raise NotImplementedError

    def switchCamera(self, anchorName):
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

    def isMaxAtmosphereLevel(self):
        raise NotImplementedError

    def isVehicleBranchEnabled(self):
        raise NotImplementedError

    def checkNyOutfit(self, outfit):
        raise NotImplementedError

    def getHangarQuestsFlagData(self):
        raise NotImplementedError

    def getHangarWidgetLinkage(self):
        raise NotImplementedError

    def getHangarEdgeColor(self):
        raise NotImplementedError

    def getSlotDescrs(self, objectName=None):
        raise NotImplementedError

    def getToyDescr(self, toyID):
        raise NotImplementedError

    def getToysByType(self, slotID):
        raise NotImplementedError

    @async
    def hangToy(self, toyID, slotID, callback):
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

    def sendSeenToys(self, toyIDs):
        raise NotImplementedError

    def sendSeenToysInCollection(self, toyIDs):
        raise NotImplementedError

    def sendViewAlbum(self, settingID, rank):
        raise NotImplementedError

    def getTalismanProgressLevel(self):
        raise NotImplementedError

    def getFreeTalisman(self):
        raise NotImplementedError

    def getTalismans(self, isInInventory=False):
        raise NotImplementedError

    def isTalismanToyTaken(self):
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

    def isOldCollectionBubbleNeeded(self, years=None):
        raise NotImplementedError

    def prepareNotifications(self, tokens):
        raise NotImplementedError


class IPianoController(IGameController):
    onLevelUp = None

    def getCurrentMusicLevel(self, check=True):
        raise NotImplementedError

    @staticmethod
    def getStatesCount():
        raise NotImplementedError

    def getSoundState(self):
        raise NotImplementedError

    def getEffectState(self):
        raise NotImplementedError

    def setInitialState(self):
        raise NotImplementedError

    def isNoMoreIdle(self):
        raise NotImplementedError

    def handlePianoClicked(self):
        raise NotImplementedError


class ITalismanSceneController(IGameController):
    onShowGiftLevelUpEffect = None
    onTalismanGiftProgressChanged = None
    onPreviewClosed = None

    def hasTalismanGiftBubble(self):
        raise NotImplementedError

    def switchToPreview(self):
        raise NotImplementedError

    def switchToHangar(self):
        raise NotImplementedError

    def switchToGift(self, talismanName):
        raise NotImplementedError

    def initialStateChanged(self):
        raise NotImplementedError

    def previewMoveTo(self, talismanName):
        raise NotImplementedError

    def previewCongratsFinished(self, talismanName):
        raise NotImplementedError

    def giftMoveTo(self, talismanName):
        raise NotImplementedError

    def setGiftAnimationState(self, talismanName, stateID):
        raise NotImplementedError

    def setPreviewAnimationState(self, talismanName, stateID):
        raise NotImplementedError

    def talismanAdded(self, entity):
        raise NotImplementedError

    def talismanAnimatorStarted(self, talismanName):
        raise NotImplementedError

    def talismanRemoved(self, entity):
        raise NotImplementedError

    def cameraAdded(self, descriptor):
        raise NotImplementedError

    def talismanPreviewAdded(self, entity):
        raise NotImplementedError

    def talismanPreviewRemoved(self, entity):
        raise NotImplementedError

    def cameraPreviewAdded(self, descriptor):
        raise NotImplementedError

    def mouseEventsAvailable(self):
        raise NotImplementedError

    def isInGiftConfirmState(self):
        raise NotImplementedError

    def setTalismansInteractive(self, isInteractive):
        raise NotImplementedError

    def setPreviewTalismansInteractive(self, isInteractive):
        raise NotImplementedError

    def isInPreview(self):
        raise NotImplementedError

    def addTalismanHoverObserver(self, observer):
        raise NotImplementedError

    def removeTalismanHoverObserver(self, listener):
        raise NotImplementedError

    def talismanToyTaken(self):
        raise NotImplementedError

    def getTalismanPosition(self, talismanName, preview=False):
        raise NotImplementedError


class ICelebritySceneController(IGameController):
    onQuestsUpdated = None
    onExitIntroScreen = None

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

    def addEdgeDetect(self):
        raise NotImplementedError

    def delEdgeDetect(self):
        raise NotImplementedError


class INewYearCraftMachineController(IGameController):
    isAntiDuplicatorOn = False
    isMegaDeviceTurnedOn = False
    selectedToyTypeIdx = 0
    selectedToySettingIdx = 0
    selectedToyRankIdx = 0

    def getSelectedToyType(self):
        raise NotImplementedError

    def calculateSelectedToyCraftCost(self):
        raise NotImplementedError

    def calculateToyCraftCost(self, isMegaToy, toyTypeIdx, toySettingIdx, toyRankIdx):
        raise NotImplementedError

    def calculateMegaToyCraftCost(self):
        raise NotImplementedError

    def getActualMegaDeviceState(self):
        raise NotImplementedError

    def getDesiredMegaDeviceState(self, isMegaDeviceTurnedOn):
        raise NotImplementedError


class IIcicleController(IGameController):

    @property
    def isCompleted(self):
        raise NotImplementedError

    @property
    def puzzleStage(self):
        raise NotImplementedError

    @property
    def isPuzzleActive(self):
        raise NotImplementedError

    def addIcicleEntity(self, icicleEntity):
        raise NotImplementedError

    def removeIcicleEntity(self, icicleEntity):
        raise NotImplementedError

    def addIlluminationEntity(self, illuminationEntity):
        raise NotImplementedError

    def removeIlluminationEntity(self, illuminationEntity):
        raise NotImplementedError

    def handleIcicleClick(self, icicleID):
        raise NotImplementedError
