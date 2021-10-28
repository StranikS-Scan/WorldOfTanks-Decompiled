# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/event_keys_counter_panel_view.py
from typing import Tuple, Dict
from frameworks.wulf import ViewSettings
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.halloween.event_keys_counter_panel_view_model import EventKeysCounterPanelViewModel, VisualTypeEnum
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.halloween.shop_view_model import PageTypeEnum
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showShopView
from helpers import dependency
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.ServerSettingsManager import UIGameEventKeys
from constants import EVENT
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()

class EventKeysCounterPanelView(ViewImpl):
    gameEventController = dependency.descriptor(IGameEventController)
    settingsCore = dependency.descriptor(ISettingsCore)
    gameSession = dependency.descriptor(IGameSessionController)
    __slots__ = ('__state', '__eventRewards', '__animateNoEnoughMoneyOnce')
    NOMONEY_ANIMATED_FOR_CURRENT_SESSION = False
    SESSION_STARTED_AT = -1

    def __init__(self, state):
        sessionStartedAt = self.gameSession.sessionStartedAt
        if EventKeysCounterPanelView.SESSION_STARTED_AT != sessionStartedAt:
            EventKeysCounterPanelView.SESSION_STARTED_AT = sessionStartedAt
            self.__resetSessionFlags()
        settings = ViewSettings(R.views.lobby.halloween.EventKeysCounterPanelView())
        settings.model = EventKeysCounterPanelViewModel()
        self.__state = state
        self.__eventRewards = self.gameEventController.getEventRewardController()
        self.__animateNoEnoughMoneyOnce = False
        super(EventKeysCounterPanelView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EventKeysCounterPanelView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            window = BackportTooltipWindow(createTooltipData(tooltip='', isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EVENT_KEY_INFO, specialArgs=[]), self.getParentWindow())
            window.load()
            return window
        super(EventKeysCounterPanelView, self).createToolTip(event)

    def _initialize(self, *args, **kwargs):
        super(EventKeysCounterPanelView, self)._initialize(*args, **kwargs)
        self._addListeners()

    def _onLoading(self):
        super(EventKeysCounterPanelView, self)._onLoading()
        self.__onUpdate()

    def _finalize(self):
        super(EventKeysCounterPanelView, self)._finalize()
        self._removeListeners()

    def _addListeners(self):
        shop = self.gameEventController.getShop()
        shop.onBundleUnlocked += self.__onBundleUpdate
        self.gameEventController.onRewardBoxKeyUpdated += self.__onUpdate
        self.viewModel.onClick += self._onClick
        g_eventBus.addListener(events.HalloweenEvent.BOX_OPENED, self.__onBoxOpened, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HalloweenEvent.BOX_SELECTED, self.__onBoxSelected, scope=EVENT_BUS_SCOPE.LOBBY)

    def _removeListeners(self):
        g_eventBus.removeListener(events.HalloweenEvent.BOX_OPENED, self.__onBoxOpened, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HalloweenEvent.BOX_SELECTED, self.__onBoxSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        shop = self.gameEventController.getShop()
        shop.onBundleUnlocked -= self.__onBundleUpdate
        self.gameEventController.onRewardBoxKeyUpdated -= self.__onUpdate
        self.viewModel.onClick -= self._onClick

    def _onClick(self):
        showShopView(PageTypeEnum.KEYS)

    def __onBoxSelected(self, event):
        selectedBoxID = event.ctx.get('boxID')
        shop = self.gameEventController.getShop()
        rewardController = self.__eventRewards
        rewardsCfg = rewardController.rewardBoxesConfig
        noMoneyForSelectedBox = selectedBoxID and rewardController.isRewardBoxRecieved(selectedBoxID) and not rewardController.isRewardBoxOpened(selectedBoxID) and shop.getKeys() < rewardsCfg[selectedBoxID].decodePrice.amount
        if noMoneyForSelectedBox:
            with self.viewModel.transaction() as model:
                model.setIsNotEnough(noMoneyForSelectedBox)

    def __onBoxOpened(self, _):
        self.__animateNoEnoughMoneyOnce = True

    def __onBundleUpdate(self, _):
        self.__onUpdate()

    def __onUpdate(self):
        shop = self.gameEventController.getShop()
        rewardsCfg = self.__eventRewards.rewardBoxesConfig
        hasNewBundle, animateForNewBundle = self.__checkNewBundles(shop)
        noMoneyForBox, animateNoEnoughMoney = self.__checkNoMoneyForNewBox(shop, rewardsCfg)
        with self.viewModel.transaction() as model:
            model.setKeys(shop.getKeys())
            model.setIsPackAvailable(hasNewBundle)
            model.setIsNotEnough(noMoneyForBox)
            model.setIsAnimated(animateForNewBundle or animateNoEnoughMoney)
            model.setState(self.__state)
        if not animateForNewBundle and animateNoEnoughMoney:
            if not self.__animateNoEnoughMoneyOnce:
                EventKeysCounterPanelView.NOMONEY_ANIMATED_FOR_CURRENT_SESSION = True
            self.__animateNoEnoughMoneyOnce = False

    def __checkNewBundles(self, shop):
        shopBundles = shop.getBundlesByShopType(EVENT.SHOP.TYPE.KEYS)
        hasNewBundle = False
        animateForNewBundle = False
        if len(shopBundles) > 1:
            lastBundle = shopBundles[-1]
            hasNewBundle = lastBundle.secondsToUnlock == 0 and not self.settingsCore.serverSettings.getGameEventStorage().get(UIGameEventKeys[lastBundle.id.upper()], False)
            animateForNewBundle = self.__state in (VisualTypeEnum.HANGAR, VisualTypeEnum.META) and hasNewBundle
        return (hasNewBundle, animateForNewBundle)

    def __checkNoMoneyForNewBox(self, shop, rewardsCfg):
        rewardBoxes = list(self.__eventRewards.iterAvailbleRewardBoxIDsInOrder())
        boxMinPriceID = -1
        if rewardBoxes:
            boxMinPriceID = min(rewardBoxes, key=lambda rID: rewardsCfg[rID].decodePrice.amount)
        noMoneyForBox = boxMinPriceID >= 0 and shop.getKeys() < rewardsCfg[boxMinPriceID].decodePrice.amount
        animateNoEnoughMoney = self.__state == VisualTypeEnum.META
        animateNoEnoughMoney = animateNoEnoughMoney and noMoneyForBox
        animateNoEnoughMoney = animateNoEnoughMoney and (self.__animateNoEnoughMoneyOnce or not EventKeysCounterPanelView.NOMONEY_ANIMATED_FOR_CURRENT_SESSION)
        return (noMoneyForBox, animateNoEnoughMoney)

    @staticmethod
    def __resetSessionFlags():
        EventKeysCounterPanelView.NOMONEY_ANIMATED_FOR_CURRENT_SESSION = False
