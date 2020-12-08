# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_helper.py
import logging
import weakref
from collections import namedtuple
import BigWorld
import ScaleformFileLoader
from gui import SystemMessages
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import getRewardTooltipContent, LootVehicleVideoRewardPresenter, LootNewYearToyPresenter, LootNewYearFragmentsCompensationPresenter, getRewardRendererModelPresenter, DEF_COMPENSATION_PRESENTERS, LootTankmanCongratsRewardPresenter, LootStyleCongratsRewardPresenter
from gui.impl.auxiliary.rewards_helper import getVehByStyleCD
from gui.impl.gen import R
from gui.impl.lobby.loot_box.loot_box_sounds import playSound, LootBoxViewEvents
from gui.impl.new_year.tooltips.toy_content import RegularToyContent, MegaToyContent
from gui.impl.pub import ViewImpl
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.shared import EVENT_BUS_SCOPE, event_dispatcher
from gui.shared import events
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import showStylePreview
from gui.shared.events import GameEvent
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency, isPlayerAccount, isMemoryRiskySystem
from items.components.ny_constants import CurrentNYConstants
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.shared import IItemsCache
MAX_PREMIUM_BOXES_TO_OPEN = 5
SpecialRewardData = namedtuple('SpecialRewardData', ('sourceName', 'congratsType', 'congratsSourceId', 'vehicleName', 'vehicleLvl', 'vehicleIsElite', 'vehicleType', 'backToSingleOpening'))
_MODEL_PRESENTERS = {'vehicles': LootVehicleVideoRewardPresenter(),
 'tmanToken': LootTankmanCongratsRewardPresenter(),
 'customizations': LootStyleCongratsRewardPresenter(),
 CurrentNYConstants.TOYS: LootNewYearToyPresenter(),
 CurrentNYConstants.TOY_FRAGMENTS: LootNewYearFragmentsCompensationPresenter()}
_logger = logging.getLogger(__name__)

def showRestrictedSysMessage():

    def _showRestrictedSysMessage():
        SystemMessages.pushMessage(text=backport.text(R.strings.lootboxes.restrictedMessage.body()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.lootboxes.restrictedMessage.header())})

    BigWorld.callback(0.0, _showRestrictedSysMessage)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, c11nService=ICustomizationService)
def showStyledVehicleByStyleCD(styleIntCD, isBackToMultiOpen=False, itemsCache=None, c11nService=None):
    _hideLootBoxWindows(isBackToMultiOpen)
    vehicle = getVehByStyleCD(styleIntCD)
    style = itemsCache.items.getItemByCD(styleIntCD)
    if vehicle.isInInventory:

        def _callback():
            c11nService.getCtx().previewStyle(style, _ExitCallback(isBackToMultiOpen))

        c11nService.showCustomization(vehicle.invID, _callback)
    else:

        def _callback():
            event_dispatcher.showHangar()
            _showLootBoxWindows(isBackToMultiOpen)

        showStylePreview(vehCD=vehicle.intCD, style=style, styleDescr=style.getDescription(), backCallback=_callback, destoryCallback=_closeLootBoxWindows, backBtnDescrLabel=backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.personalAwards()))


class LootBoxShowHideCloseHandler(object):
    __slots__ = ('__target', '__isHidden')

    def __init__(self):
        self.__target = None
        self.__isHidden = False
        return

    @property
    def isHidden(self):
        return self.__isHidden

    def startListen(self, target):
        self.__target = weakref.proxy(target)
        g_eventBus.addListener(GameEvent.HIDE_LOOT_BOX_WINDOWS, self.__onHideLBWindow)
        g_eventBus.addListener(GameEvent.SHOW_LOOT_BOX_WINDOWS, self.__onShowLBWindow)
        g_eventBus.addListener(GameEvent.CLOSE_LOOT_BOX_WINDOWS, self.__onCloseLBWindow)

    def stopListen(self):
        self.__target = None
        self.__isHidden = False
        g_eventBus.removeListener(GameEvent.HIDE_LOOT_BOX_WINDOWS, self.__onHideLBWindow)
        g_eventBus.removeListener(GameEvent.SHOW_LOOT_BOX_WINDOWS, self.__onShowLBWindow)
        g_eventBus.removeListener(GameEvent.CLOSE_LOOT_BOX_WINDOWS, self.__onCloseLBWindow)
        return

    def __onHideLBWindow(self, _=None):
        if self.__target:
            self.__isHidden = True
            self.__target.hide()

    def __onShowLBWindow(self, _=None):
        if self.__target:
            self.__isHidden = False
            self.__target.show()
            fireSpecialRewardsClosed()

    def __onCloseLBWindow(self, _=None):
        if self.__target:
            self.__isHidden = False
            self.__target.destroy()


class LootBoxHideableView(ViewImpl):
    __slots__ = ('_showHideCloseHandler', '_isMemoryRiskySystem', '_hideCompleteCallback', '_isCanClose', '__videoFiles', '__invokeFinalize')
    _VIDEOS = []

    def __init__(self, settings):
        self._isMemoryRiskySystem = isMemoryRiskySystem()
        self._isCanClose = not self._isMemoryRiskySystem
        self.__videoFiles = self.__getVideoFiles()
        self.__invokeFinalize = False
        if self.__videoFiles:
            ScaleformFileLoader.enableStreaming(self.__videoFiles)
        super(LootBoxHideableView, self).__init__(settings)
        self._hideCompleteCallback = None
        self._showHideCloseHandler = LootBoxShowHideCloseHandler()
        return

    def canBeClosed(self):
        return not self._showHideCloseHandler.isHidden

    def _initialize(self):
        super(LootBoxHideableView, self)._initialize()
        self._showHideCloseHandler.startListen(self.getParentWindow())

    def _finalize(self):
        if not self.__invokeFinalize and self.__videoFiles:
            ScaleformFileLoader.disableStreaming()
        if self._hideCompleteCallback is not None:
            self._hideCompleteCallback = None
        self._showHideCloseHandler.stopListen()
        self._showHideCloseHandler = None
        g_eventBus.removeListener(events.LootboxesEvent.HIDE_COMPLETE, self._onHideCompleteCallback, scope=EVENT_BUS_SCOPE.LOBBY)
        super(LootBoxHideableView, self)._finalize()
        return

    def _startFade(self, callback, withPause=True):
        if callback is not None:
            self._hideCompleteCallback = callback
        if self.__videoFiles:
            ScaleformFileLoader.disableStreaming()
            self.__invokeFinalize = True
        g_eventBus.addListener(events.LootboxesEvent.HIDE_COMPLETE, self._onHideCompleteCallback, scope=EVENT_BUS_SCOPE.LOBBY)
        showLootboxFadeWindow(withPause)
        return

    def _onHideCompleteCallback(self, _=None):
        g_eventBus.removeListener(events.LootboxesEvent.HIDE_COMPLETE, self._onHideCompleteCallback, scope=EVENT_BUS_SCOPE.LOBBY)
        if self._hideCompleteCallback is not None:
            self._hideCompleteCallback()
            self._hideCompleteCallback = None
        return

    def _getVideosList(self):
        return []

    def _setIsCanClose(self, value):
        self._isCanClose = value

    def __getVideoFiles(self):
        return [ '/videos/'.join((SCALEFORM_SWF_PATH_V3, videoName)) for videoName in self._getVideosList() ]


def showLootboxFadeWindow(withPause=True):
    from gui.impl.lobby.loot_box.loot_box_fade_view import LootBoxFadeWindow
    rewardWindow = LootBoxFadeWindow(withPause)
    rewardWindow.load()


def getLootboxRendererModelPresenter(reward):
    return getRewardRendererModelPresenter(reward, _MODEL_PRESENTERS, DEF_COMPENSATION_PRESENTERS)


def showLootBoxPremiumMultiOpen(lootBoxItem, rewards, boxesToOpen, parent=None):
    from gui.impl.lobby.loot_box.loot_box_premium_multi_open_view import LootBoxPremiumMultiOpenWindow
    window = LootBoxPremiumMultiOpenWindow(lootBoxItem, rewards, boxesToOpen, parent)
    window.load()


def showLootBoxMultiOpen(lootBoxItem, rewards, countToOpen, parent=None):
    from gui.impl.lobby.loot_box.loot_box_multi_open_view import LootBoxMultiOpenWindow
    window = LootBoxMultiOpenWindow(lootBoxItem, rewards, countToOpen, parent)
    window.load()


def showLootBoxReward(lootBoxItem, rewards, parent=None, isBackward=False):
    from gui.impl.lobby.loot_box.loot_box_opening_view import LootBoxOpeningWindow
    from gui.impl.lobby.loot_box.loot_box_reward_view import LootBoxRewardWrapperWindow
    rewardWindow = LootBoxRewardWrapperWindow(lootBoxItem, rewards, parent, isBackward)
    openingWindow = LootBoxOpeningWindow(rewardWindow)
    rewardWindow.load()
    openingWindow.load()


def fireHideRewardView():
    g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_REWARD_VIEW_CLOSED), EVENT_BUS_SCOPE.LOBBY)


def fireCloseToHangar():
    playSound(LootBoxViewEvents.ENTRY_VIEW_EXIT)
    _closeLootBoxWindows()


def fireHideMultiOpenView():
    g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_MULTI_OPEN_VIEW_CLOSED), EVENT_BUS_SCOPE.LOBBY)


def fireSpecialRewardsClosed():
    g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_SHOW_SPECIAL_REWARDS_CLOSED), EVENT_BUS_SCOPE.LOBBY)


def showLootBoxSpecialReward(responseDict, parent=None):
    from gui.impl.lobby.loot_box.loot_box_special_reward_view import LootBoxSpecialRewardWindow
    congratsType = responseDict.get('congratsType')
    congratsSourceId = responseDict.get('congratsSourceId')
    sourceName = responseDict.get('sourceName')
    if sourceName and congratsSourceId is not None and congratsType is not None:
        specialRewardData = SpecialRewardData(sourceName=sourceName, congratsType=congratsType, congratsSourceId=int(congratsSourceId), vehicleName=responseDict.get('vehicleName'), vehicleIsElite=responseDict.get('vehicleIsElite'), vehicleLvl=responseDict.get('vehicleLvl'), vehicleType=responseDict.get('vehicleType'), backToSingleOpening=responseDict.get('backToSingleOpening'))
        window = LootBoxSpecialRewardWindow(specialRewardData, parent)
        window.load()
    return


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isLootboxValid(boxType, itemsCache=None):
    return any((box.getType() == boxType for box in itemsCache.items.tokens.getLootBoxes().itervalues()))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getLootBoxByTypeAndCategory(boxType, boxCategory=None, isInInventory=False, itemsCache=None):
    boxes = itemsCache.items.tokens.getLootBoxes().values()
    for box in boxes:
        if box.getType() == boxType and (not isInInventory or box.getInventoryCount() > 0):
            isCommonBox = boxType == NewYearLootBoxes.COMMON
            if boxType == NewYearLootBoxes.PREMIUM and boxCategory == box.getCategory() or isCommonBox:
                return box

    return None


def getTooltipContent(event, storedTooltipData):
    tooltipContent = getRewardTooltipContent(event, storedTooltipData)
    if tooltipContent is not None:
        return tooltipContent
    tooltipContentRes = R.views.lobby.new_year.tooltips
    if event.contentID == tooltipContentRes.ny_regular_toy_tooltip_content.NyRegularToyTooltipContent():
        toyID = event.getArgument('toyID')
        return RegularToyContent(toyID, False)
    elif event.contentID == tooltipContentRes.ny_mega_toy_tooltip_content.NyMegaToyTooltipContent():
        toyID = event.getArgument('toyID')
        return MegaToyContent(toyID, False)
    else:
        return


def worldDrawEnabled(value):
    if isPlayerAccount():
        BigWorld.worldDrawEnabled(value)


class _ExitCallback(object):
    _c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self, isBackToMultiOpen=False):
        self.__wasCalled = False
        self.__isBackToMultiOpen = isBackToMultiOpen

    def apply(self):
        if not self.__wasCalled:
            _showLootBoxWindows(self.__isBackToMultiOpen)
            self.__wasCalled = True

    def close(self):
        if not self.__wasCalled:
            self._c11nService.getCtx().events.onCloseWindow(force=True)
            _showLootBoxWindows(self.__isBackToMultiOpen)
            self.__wasCalled = True

    def destroy(self):
        if not self.__wasCalled:
            _closeLootBoxWindows()
            self.__wasCalled = True


@dependency.replace_none_kwargs(festivityController=IFestivityController)
def _showLootBoxWindows(isBackToMultiOpen=False, festivityController=None):
    if isMemoryRiskySystem() and not isBackToMultiOpen:
        if not festivityController.isEnabled():
            return
        showLootboxFadeWindow()
        showLootBoxReward(None, None, None, True)
    else:
        if not isMemoryRiskySystem():
            playSound(LootBoxViewEvents.ENTRY_VIEW_ENTER)
        g_eventBus.handleEvent(GameEvent(GameEvent.SHOW_LOOT_BOX_WINDOWS))
        worldDrawEnabled(False)
    return


def _hideLootBoxWindows(isBackToMultiOpen=False):
    worldDrawEnabled(True)
    isRiskySystem = isMemoryRiskySystem()
    if isRiskySystem and not isBackToMultiOpen:
        return
    if not isRiskySystem:
        playSound(LootBoxViewEvents.ENTRY_VIEW_EXIT)
    g_eventBus.handleEvent(GameEvent(GameEvent.HIDE_LOOT_BOX_WINDOWS))


def _closeLootBoxWindows():
    worldDrawEnabled(True)
    g_eventBus.handleEvent(GameEvent(GameEvent.CLOSE_LOOT_BOX_WINDOWS))
