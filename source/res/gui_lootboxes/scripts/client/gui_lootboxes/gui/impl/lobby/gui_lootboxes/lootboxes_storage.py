# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/lootboxes_storage.py
import logging
from collections import defaultdict
from functools import partial
import typing
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootboxes_storage_view_model import LootboxesStorageViewModel, States
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.sound import LOOT_BOXES_SOUND_SPACE
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.sound import playEnterSound
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.bonus_group_tooltip import BonusGroupTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.guaranteed_reward_tooltip import GuaranteedRewardTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_key_tooltip import LootboxKeyTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip_rotation import LootboxRotationTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.probability_button_tooltip import ProbabilityButtonTooltip
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.unique_rewards_view import getUniqueRewardHandler
from gui_lootboxes.gui.shared.event_dispatcher import showLootBoxOpenErrorWindow, showBonusProbabilitiesWindow, showRewardScreenWindow
from gui_lootboxes.gui.shared.events import LootBoxesEvent
from gui_lootboxes.gui.shared.gui_helpers import getLootBoxViewModel, getLootBoxKeyViewModel
from gui_lootboxes.gui.storage_context.context import LootBoxesContext, ViewEvents, ReturnPlaces
from account_helpers.AccountSettings import LOOT_BOXES_OPEN_ANIMATION_ENABLED, LOOT_BOXES_LAST_ADDED_ID, KEY_LOOTBOX_TRIGGER_HINT_SHOWN
from frameworks.wulf import ViewSettings, ViewStatus, WindowFlags, WindowLayer
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.lobby.loot_box.loot_box_helper import getKeyByID
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.shared.gui_items.loot_box import LootBoxKey
from helpers import dependency
from helpers.func_utils import waitEventAndCall
from lootboxes_common import makeLootboxTokenID, makeLBKeyTokenID
from shared_utils import findFirst
from skeletons.gui.game_control import IGuiLootBoxesController, IGuiLootBoxesIntroController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from wg_async import AsyncEvent
if typing.TYPE_CHECKING:
    import Event
    from frameworks.state_machine import StringEvent
    from frameworks.wulf import ViewEvent, View
_logger = logging.getLogger(__name__)

class LootBoxesStorageView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __guiLootBoxesCtr = dependency.descriptor(IGuiLootBoxesController)
    __guiLootBoxesIntroCtr = dependency.descriptor(IGuiLootBoxesIntroController)
    __guiLoader = dependency.descriptor(IGuiLoader)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _COMMON_SOUND_SPACE = LOOT_BOXES_SOUND_SPACE
    _REWARD_SCREEN = R.views.gui_lootboxes.lobby.gui_lootboxes.LootboxRewardsView()
    _ERROR_SCREEN = R.views.gui_lootboxes.lobby.gui_lootboxes.OpenBoxErrorView()
    _LOSE_REWARD_SCREEN = R.views.gui_lootboxes.lobby.gui_lootboxes.LootBoxesLoseRewardScreen()
    _CHILD_VIEWS = (_ERROR_SCREEN, _REWARD_SCREEN, _LOSE_REWARD_SCREEN)
    __slots__ = ('__context', '__currentLootBoxId', '__openingAnimEvent', '__uniqueRewardsViewId', '__uniqueRewardsViewClosedEvent', '__waitStatesHandlers', '__returnPlace', '__initialLootBox', '__closeCallback', '__infoPageUrl')

    def __init__(self, layoutID, returnPlace=ReturnPlaces.TO_HANGAR, initialLootBox=0, closeCallback=None):
        settings = ViewSettings(layoutID)
        settings.model = LootboxesStorageViewModel()
        super(LootBoxesStorageView, self).__init__(settings)
        self.__context = LootBoxesContext()
        self.__initialLootBox = initialLootBox
        self.__currentLootBoxId = 0
        self.__openingAnimEvent = AsyncEvent(scope=self.__context.getAsyncScope())
        self.__uniqueRewardsViewClosedEvent = AsyncEvent(scope=self.__context.getAsyncScope())
        self.__waitStatesHandlers = defaultdict(list)
        self.__uniqueRewardsViewId = 0
        self.__returnPlace = ReturnPlaces(returnPlace)
        self.__closeCallback = closeCallback
        self.__infoPageUrl = None
        return

    @property
    def viewModel(self):
        return super(LootBoxesStorageView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.BonusGroupTooltip():
            bonusGroup = event.getArgument('bonusGroup')
            lootBoxID = event.getArgument('lootBoxID')
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            return BonusGroupTooltip(bonusGroup, lootBox.getBonusesByGroup(bonusGroup), lootBox.getCategory())
        elif contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.ProbabilityButtonTooltip():
            return ProbabilityButtonTooltip()
        elif contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxRotationTooltip():
            lootBoxID = event.getArgument('lootBoxID')
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            return LootboxRotationTooltip(lootBox)
        elif contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip():
            lootBoxID = event.getArgument('lootBoxID')
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            return LootboxTooltip(lootBox)
        elif contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.GuaranteedRewardTooltip():
            lootBoxID = event.getArgument('lootBoxID')
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            return GuaranteedRewardTooltip(lootBox)
        else:
            if contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxKeyTooltip():
                keyID = event.getArgument('keyID')
                key = getKeyByID(int(keyID))
                if key is not None:
                    isActionTooltip = event.getArgument('isActionTooltip')
                    isShowCount = event.getArgument('isShowCount')
                    return LootboxKeyTooltip(key=key, isActionTooltip=isActionTooltip, isShowCount=isShowCount if isShowCount is not None else True)
            return super(LootBoxesStorageView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(LootBoxesStorageView, self)._onLoading(*args, **kwargs)
        self.__context.init()
        with self.viewModel.transaction() as model:
            self.__fillLootBoxesModel(model=model)
            self.__fillLootBoxKeysModel(model=model)
            self.__setMainData(model=model)
            model.setCurrentState(self.__context.getCurrentState())
            showTriggerHint = self.__guiLootBoxesCtr.hasLootboxKey() and not self.__guiLootBoxesCtr.getSetting(KEY_LOOTBOX_TRIGGER_HINT_SHOWN)
            if showTriggerHint:
                model.setIsShowTriggerHint(self.__guiLootBoxesCtr.hasLootboxKey() and not self.__guiLootBoxesCtr.getSetting(KEY_LOOTBOX_TRIGGER_HINT_SHOWN))
                self.__guiLootBoxesCtr.setSetting(KEY_LOOTBOX_TRIGGER_HINT_SHOWN, True)
        self.__guiLootBoxesIntroCtr.tryShowIntro()

    def _onLoaded(self, *args, **kwargs):
        super(LootBoxesStorageView, self)._onLoaded(*args, **kwargs)
        self.__context.viewReady()
        playEnterSound(self.__guiLootBoxesCtr.isFirstStorageEnter())
        self.__guiLootBoxesCtr.setStorageVisited()

    def _finalize(self):
        super(LootBoxesStorageView, self)._finalize()
        self.__context.fini()
        self.__waitStatesHandlers.clear()

    def _getListeners(self):
        return ((LootBoxesEvent.OPEN_LOOTBOXES, self.__repeatopenLootBoxes, EVENT_BUS_SCOPE.LOBBY),)

    def _getEvents(self):
        return ((self.__guiLoader.windowsManager.onViewStatusChanged, self.__onViewStatusChanged),
         (self.__context.onStateChanged, self.__handleStateChanged),
         (self.__guiLootBoxesCtr.onAvailabilityChange, self.__onAvailabilityChange),
         (self.__guiLootBoxesCtr.onStatusChange, self.__onStatusChange),
         (self.__guiLootBoxesCtr.onBoxesCountChange, self.__onBoxesCountChange),
         (self.__guiLootBoxesCtr.onKeysUpdate, self.__onKeysUpdate),
         (self.__guiLootBoxesCtr.onBoxInfoUpdated, self.__onBoxInfoUpdated),
         (self.viewModel.onLootboxSelected, self.__onLootboxSelected),
         (self.viewModel.openLootBoxes, self.__openLootBoxes),
         (self.viewModel.openningFinished, self.__openningFinished),
         (self.viewModel.changeAnimationEnabledSetting, self.__changeAnimationEnabledSetting),
         (self.viewModel.buyBox, self.__onBuyBox),
         (self.viewModel.showBonusProbabilities, self.__showBonusProbabilities),
         (self.viewModel.hideTriggerHint, self.__hideTriggerHint),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onError, self.onError),
         (self.viewModel.showLootBoxInfoPage, self.__showLootBoxInfoPage))

    def __onLootboxSelected(self, args):
        lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(args.get('lootBoxID', 0)))
        if lootBox is not None and lootBox.isVisibleInStorage():
            self.__selectLootBox(lootBox.getID())
        return

    @replaceNoneKwargsModel
    def __selectLootBox(self, lootBoxID, model=None):
        if self.__context.getCurrentState() != States.STORAGE_VIEWING or lootBoxID == self.__currentLootBoxId:
            return
        self.__currentLootBoxId = lootBoxID
        model.setCurrentLootboxID(lootBoxID)
        model.setIsShowInfoButton(self.__checkIfHasInfoPage())

    def __repeatopenLootBoxes(self, event):
        self.__openLootBoxes(event.ctx)

    def __openLootBoxes(self, args):
        if self.__context.getCurrentState() not in (States.STORAGE_VIEWING, States.REWARDING):
            return
        lootBoxID = int(args.get('lootBoxID', 0))
        count = int(args.get('count', 1))
        keyID = int(args.get('keyID', 0))
        lootBox = self.__itemsCache.items.tokens.getLootBoxByID(lootBoxID)
        self.__context.postViewEvent(ViewEvents.ON_OPEN_CLICK, (lootBox, count, keyID))

    def __openningFinished(self):
        self.__openingAnimEvent.set()

    def __onBuyBox(self):
        if self.__guiLootBoxesCtr.isBuyAvailable():
            self.__context.setReturnPlace(ReturnPlaces.TO_SHOP)
            self.destroyWindow()
            self.__guiLootBoxesCtr.openShop(self.__currentLootBoxId)

    def __onClose(self):
        self.__context.setReturnPlace(self.__returnPlace)
        if self.__closeCallback:
            self.__closeCallback()
        self.destroyWindow()

    def onError(self, args):
        errorFilePath = str(args.get('errorFilePath', ''))
        _logger.error('Lootbox video error: %s', errorFilePath)

    @replaceNoneKwargsModel
    def __fillLootBoxesModel(self, model=None):
        lbArray = model.getLootboxes()
        lbArray.clear()
        lootBoxes = sorted(self.__guiLootBoxesCtr.getGuiLootBoxes())
        if not self.__currentLootBoxId:
            if self.__initialLootBox:
                box = self.__itemsCache.items.tokens.getLootBoxByTokenID(makeLootboxTokenID(self.__initialLootBox))
                if box and box.isVisibleInStorage():
                    self.__selectLootBox(self.__initialLootBox, model=model)
                self.__initialLootBox = 0
            else:
                lastAddedLootBoxID = self.__guiLootBoxesCtr.getSetting(LOOT_BOXES_LAST_ADDED_ID)
                lastAddedLootBox = findFirst(lambda lootBox: lootBox.getID() == lastAddedLootBoxID, lootBoxes)
                if lastAddedLootBox is not None and lastAddedLootBox.isVisibleInStorage():
                    self.__selectLootBox(lastAddedLootBoxID, model=model)
        for lootbox in lootBoxes:
            if lootbox is not None and lootbox.isVisibleInStorage():
                attemptsAfterGuaranteed = self.__itemsCache.items.tokens.getAttemptsAfterGuaranteedRewards(lootbox)
                lbArray.addViewModel(getLootBoxViewModel(lootbox, attemptsAfterGuaranteed))
                if not self.__currentLootBoxId:
                    self.__selectLootBox(lootbox.getID(), model=model)

        lbArray.invalidate()
        return

    @replaceNoneKwargsModel
    def __fillLootBoxKeysModel(self, model=None):
        keyArray = model.getLootboxKeys()
        keyArray.clear()
        for keyID, keyConfig in self.__lobbyContext.getServerSettings().getLootBoxKeyConfig().iteritems():
            keyToken = makeLBKeyTokenID(keyID)
            keyItem = LootBoxKey(keyToken, self.__itemsCache.items.tokens.getTokenCount(keyToken), keyConfig)
            keyArray.addViewModel(getLootBoxKeyViewModel(keyItem))

        keyArray.invalidate()

    @replaceNoneKwargsModel
    def __setMainData(self, model=None):
        model.setIsAnimationEnabled(self.__guiLootBoxesCtr.getSetting(LOOT_BOXES_OPEN_ANIMATION_ENABLED))
        model.setIsBuyAvailable(self.__guiLootBoxesCtr.isBuyAvailable())
        model.setReturnPlace(ReturnPlaces(self.__returnPlace))

    def __handleStateChanged(self, state, event):
        self.viewModel.setCurrentState(States(state))
        for handler in self.__waitStatesHandlers.pop(States(state), ()):
            handler()

        if self.viewStatus in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
            return
        else:
            if state == States.OPENING_ERROR.value:
                showLootBoxOpenErrorWindow(parent=self.getParentWindow())
            elif state == States.OPENING.value or state == States.LOSE_OPENING.value:
                result = event.getArgument('result', None)
                resultData = result.auxData if result else {}
                waitEventAndCall(self.__openingAnimEvent, partial(self.__context.postViewEvent, ViewEvents.ON_OPENING_FINISH, (getUniqueRewardHandler(resultData), resultData.get('bonus', []), resultData.get('clientData', {}))))
            elif state == States.REWARDING.value:
                rewards = event.getArgument('rewards', None)
                clientData = event.getArgument('clientData', {})
                lootBox = self.__itemsCache.items.tokens.getLootBoxByID(self.__currentLootBoxId)
                if lootBox and rewards:
                    showRewardScreenWindow(rewards, lootBox, clientData, parent=self.getParentWindow())
                else:
                    self.__context.postViewEvent(ViewEvents.ON_CHILD_VIEW_SKIP, None)
                self.__openingAnimEvent.clear()
            elif state == States.UNIQUE_REWARDING.value:
                uniqueRewardsHandler = event.getArgument('uniqueRewardsHandler', None)
                rewards = event.getArgument('rewards', None)
                clientData = event.getArgument('clientData', 0)
                if uniqueRewardsHandler and uniqueRewardsHandler.getRewardsViewID():
                    self.__uniqueRewardsViewClosedEvent.clear()
                    uniqueRewardsHandler.showRewardsWindow(parent=self.getParentWindow())
                    self.__uniqueRewardsViewId = uniqueRewardsHandler.getRewardsViewID()
                    waitEventAndCall(self.__uniqueRewardsViewClosedEvent, partial(self.__context.postViewEvent, ViewEvents.ON_CHILD_VIEW_CLOSED, (rewards, clientData)))
                else:
                    self.__context.postViewEvent(ViewEvents.ON_CHILD_VIEW_SKIP, event.getArgument('rewards', None))
            elif state == States.STORAGE_VIEWING.value:
                self.__openingAnimEvent.clear()
            return

    def __onViewStatusChanged(self, uniqueID, newStatus):
        if newStatus == ViewStatus.DESTROYING:
            view = self.__guiLoader.windowsManager.getView(uniqueID)
            if view is not None and view.layoutID == self.__uniqueRewardsViewId:
                self.__uniqueRewardsViewClosedEvent.set()
                self.__uniqueRewardsViewId = 0
            elif view is not None and view.layoutID in self._CHILD_VIEWS:
                self.__context.postViewEvent(ViewEvents.ON_CHILD_VIEW_CLOSED, None)
        return

    def __onAvailabilityChange(self, *_):
        if not self.__guiLootBoxesCtr.isLootBoxesAvailable():
            if self.__context.getCurrentState() == States.STORAGE_VIEWING:
                self.destroyWindow()
            else:
                self.__waitStatesHandlers[States.STORAGE_VIEWING].append(self.destroyWindow)

    def __onStatusChange(self):
        if self.__guiLootBoxesCtr.isEnabled() and self.__guiLootBoxesCtr.isLootBoxesAvailable():
            self.__setMainData()
        elif self.__context.getCurrentState() == States.STORAGE_VIEWING:
            self.destroyWindow()
        else:
            self.__waitStatesHandlers[States.STORAGE_VIEWING].append(self.destroyWindow)

    def __onBoxesCountChange(self, *_):
        if self.__context.getCurrentState() == States.STORAGE_VIEWING:
            if self.viewStatus in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
                return
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(self.__currentLootBoxId)
            if lootBox is None or not lootBox.isVisibleInStorage():
                self.__currentLootBoxId = 0
            self.__fillLootBoxesModel()
            if not self.__currentLootBoxId:
                self.viewModel.setCurrentLootboxID(0)
        else:
            self.__waitStatesHandlers[States.STORAGE_VIEWING].append(self.__onBoxesCountChange)
        return

    def __onKeysUpdate(self, *_):
        if self.__context.getCurrentState() in (States.OPENING, States.LOSE_OPENING, States.STORAGE_VIEWING):
            if self.viewStatus in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
                return
            self.__fillLootBoxKeysModel()
            self.__waitStatesHandlers[States.STORAGE_VIEWING].append(self.__onBoxInfoUpdated)

    def __onBoxInfoUpdated(self):
        if self.__context.getCurrentState() == States.STORAGE_VIEWING:
            self.__fillLootBoxesModel()

    def __changeAnimationEnabledSetting(self, args):
        isEnabled = args.get('enabled', None)
        if isEnabled is not None and self.__guiLootBoxesCtr.getSetting(LOOT_BOXES_OPEN_ANIMATION_ENABLED) != isEnabled and self.__context.getCurrentState() == States.STORAGE_VIEWING:
            self.__guiLootBoxesCtr.setSetting(LOOT_BOXES_OPEN_ANIMATION_ENABLED, isEnabled)
            self.viewModel.setIsAnimationEnabled(isEnabled)
        return

    def __showBonusProbabilities(self):
        lootBox = self.__itemsCache.items.tokens.getLootBoxByID(self.__currentLootBoxId)
        if lootBox is not None:
            showBonusProbabilitiesWindow(lootBox, parent=self.getParentWindow())
        return

    def __hideTriggerHint(self):
        self.__guiLootBoxesCtr.setSetting(KEY_LOOTBOX_TRIGGER_HINT_SHOWN, True)

    def __checkIfHasInfoPage(self):
        lootBox = self.__itemsCache.items.tokens.getLootBoxByID(self.__currentLootBoxId)
        lootBoxCategory = lootBox.getCategory()
        self.__infoPageUrl = self.__getInfoPageURL(lootBoxCategory)
        return bool(self.__infoPageUrl)

    def __showLootBoxInfoPage(self):
        showBrowserOverlayView(self.__infoPageUrl, VIEW_ALIAS.OVERLAY_WEB_STORE)

    def __getInfoPageURL(self, lootBoxUrl):
        infoPageURL = GUI_SETTINGS.lookup('lootBoxInfoPageURL')
        return infoPageURL.get(lootBoxUrl) if infoPageURL else None


class LootBoxesStorageWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, returnPlace=ReturnPlaces.TO_HANGAR, initialLootBox=0, closeCallback=None):
        super(LootBoxesStorageWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=LootBoxesStorageView(R.views.gui_lootboxes.lobby.gui_lootboxes.StorageView(), returnPlace, initialLootBox, closeCallback), layer=WindowLayer.TOP_WINDOW)
