# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/festival/festival_main_view.py
import GUI
from account_helpers.AccountSettings import AccountSettings, FESTIVAL_SHOP_VISITED, FESTIVAL_REWARDS_VISITED, FESTIVAL_INFO_VISITED
from async import await, async
from festivity.festival.constants import FestSyncDataKeys
from festivity.festival.hint_helper import FestivalHintHelper
from festivity.festival.sounds import playSound
from frameworks.wulf import ViewFlags
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.builders import ResSimpleDialogBuilder
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.festival.festival_main_view_model import FestivalMainViewModel
from gui.impl.gen.view_models.views.lobby.festival.festival_tab_model import FestivalTabModel
from gui.impl.lobby.festival.festival_card_view import FestivalCardView
from gui.impl.lobby.festival.festival_helper import FestivalViews
from gui.impl.lobby.festival.festival_rewards_view import FestivalRewardsView
from gui.impl.lobby.festival.festival_info_view import FestivalInfoView
from gui.impl.lobby.festival.festival_shop_view import FestivalShopView
from gui.impl.lobby.festival.festival_tickets_tooltip import FestivalTicketsTooltip
from gui.impl.lobby.festival.festival_tutorial_video_view import FestivalTutorialVideoViewWindow
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showHangar
from gui.shared.events import LobbyHeaderMenuEvent
from helpers import dependency
from skeletons.festival import IFestivalController
_FESTIVAL_VIEW_CONTENTS = {FestivalViews.REWARDS: FestivalRewardsView,
 FestivalViews.SHOP: FestivalShopView,
 FestivalViews.INFO: FestivalInfoView}
_BLUR_IN_TIME = 0.65
_BLUR_OUT_TIME = 1.1

class FestivalContentsNotificator(object):
    __festController = dependency.descriptor(IFestivalController)
    __slots__ = ('__contentMethods',)

    def __init__(self):
        self.__contentMethods = {FestivalViews.SHOP: self.getShopNotification,
         FestivalViews.REWARDS: self.__getRewardsNotification,
         FestivalViews.INFO: self.__getInfoNotification,
         FestivalViews.CARD: self.__getCardNotification}

    def updateTabModel(self, tabModels):
        for tabModel in tabModels:
            tabModel.setUnseenCount(0 if self.__contentMethods[tabModel.getName()]() else 1)

        tabModels.invalidate()

    def clear(self):
        self.__contentMethods = None
        return

    def getShopNotification(self):
        return AccountSettings.getNotifications(FESTIVAL_SHOP_VISITED) if self.__festController.isCommonItemCollected() else True

    @staticmethod
    def __getRewardsNotification():
        return AccountSettings.getNotifications(FESTIVAL_REWARDS_VISITED)

    @staticmethod
    def __getInfoNotification():
        return AccountSettings.getNotifications(FESTIVAL_INFO_VISITED)

    def __getCardNotification(self):
        return not bool(self.__festController.getUnseenItems())


class FestivalMainView(ViewImpl):
    __festController = dependency.descriptor(IFestivalController)
    __slots__ = ('__blur', '__contentNotificator')

    def __init__(self, viewKey=R.views.lobby.festival.festival_main_view.FestivalMainView(), *args, **kwargs):
        super(FestivalMainView, self).__init__(viewKey, ViewFlags.LOBBY_SUB_VIEW, FestivalMainViewModel, *args, **kwargs)
        self.__blur = GUI.WGUIBackgroundBlur()
        self.__contentNotificator = None
        return

    @property
    def viewModel(self):
        return super(FestivalMainView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return FestivalTicketsTooltip(self.viewModel.getTicketsStr()) if contentID == R.views.lobby.festival.festival_tickets_tooltip.FestivalTicketsTooltip() else super(FestivalMainView, self).createToolTipContent(event=event, contentID=contentID)

    def switchContent(self, viewName):
        currentViewName = self.viewModel.getCurrentView()
        if currentViewName == viewName:
            return
        self.viewModel.setStartIndex(FestivalViews.ALL.index(currentViewName))
        with self.viewModel.transaction() as model:
            self.__setContent(viewName, model)
            model.setStartIndex(FestivalViews.ALL.index(viewName))

    def _initialize(self, viewName):
        super(FestivalMainView, self)._initialize()
        g_eventBus.handleEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': True}), EVENT_BUS_SCOPE.LOBBY)
        self.__contentNotificator = FestivalContentsNotificator()
        if not self.__contentNotificator.getShopNotification():
            viewName = FestivalViews.SHOP
        with self.viewModel.transaction() as model:
            model.setFirstEntering(not FestivalHintHelper.getFirstEntry())
            model.setStartIndex(FestivalViews.ALL.index(viewName))
            viewNames = model.getViews()
            for name in FestivalViews.ALL:
                viewModel = FestivalTabModel()
                viewModel.setName(name)
                viewNames.addViewModel(viewModel)

            viewNames.invalidate()
            self.__updateTickets(model)
            self.__updateItems(model)
            self.__updateNotificationOnTab(model)
            model.setCustomizationCardView(FestivalCardView())
        self.__setContent(viewName, self.viewModel)
        self.viewModel.onSwitchContent += self.__onSwitchContent
        self.viewModel.onCloseBtnClicked += self.__onCloseBtnClicked
        self.viewModel.onCardInfoClicked += self.__showCardInfoVideo
        self.__festController.onDataUpdated += self.__onDataUpdated
        self.__festController.onStateChanged += self.__onStateChanged
        AccountSettings.onSettingsChanging += self.__onAccountSettingsChanged
        self.__blur.fadeTime = _BLUR_IN_TIME
        self.__blur.enable = True
        playSound(backport.sound(R.sounds.ev_fest_hangar_token_enter()))

    def _finalize(self):
        playSound(backport.sound(R.sounds.ev_fest_hangar_token_exit()))
        self.viewModel.onSwitchContent -= self.__onSwitchContent
        self.viewModel.onCloseBtnClicked -= self.__onCloseBtnClicked
        self.__festController.onDataUpdated -= self.__onDataUpdated
        self.__festController.onStateChanged -= self.__onStateChanged
        self.viewModel.onCardInfoClicked -= self.__showCardInfoVideo
        AccountSettings.onSettingsChanging -= self.__onAccountSettingsChanged
        g_eventBus.handleEvent(LobbyHeaderMenuEvent(LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        self.__contentNotificator.clear()
        super(FestivalMainView, self)._finalize()
        self.__blur.fadeTime = _BLUR_OUT_TIME
        self.__blur.enable = False
        self.__blur = None
        return

    def __onDataUpdated(self, keys):
        with self.viewModel.transaction() as model:
            if FestSyncDataKeys.TICKETS in keys:
                self.__updateTickets(model)
            if FestSyncDataKeys.ITEMS in keys:
                self.__updateItems(model)
            if FestSyncDataKeys.SEEN_ITEMS in keys or FestSyncDataKeys.ITEMS in keys:
                self.__updateNotificationOnTab(model)

    def __onStateChanged(self):
        if not self.__festController.isEnabled():
            self.__destroyWindow()

    def __onSwitchContent(self, args):
        viewName = args['view']
        with self.viewModel.transaction() as model:
            self.__setContent(viewName, model)

    @async
    def __onCloseBtnClicked(self, *_):
        customizationCardView = self.viewModel.getCustomizationCardView()
        needQuit = True
        if customizationCardView.isNotApplied():
            builder = ResSimpleDialogBuilder()
            builder.setMessagesAndButtons(R.strings.festival.dialogs.exitCustomization, R.strings.festival.dialogs.exitCustomization)
            builder.setBlur(enableBlur3dScene=False)
            dialogWindow = builder.build(self)
            needQuit = yield await(dialogs.showSimple(dialogWindow))
        if needQuit:
            self.__destroyWindow()
        else:
            self.viewModel.setTriggerRestoreAlpha(not self.viewModel.getTriggerRestoreAlpha())

    def __showCardInfoVideo(self, *_):
        FestivalTutorialVideoViewWindow(parent=self.getParentWindow()).load()
        FestivalHintHelper.setFirstEntry()
        self.__updateRndBuyHint()

    def __destroyWindow(self):
        showHangar()
        self.destroyWindow()

    def __updateTickets(self, model):
        ticketsCount = self.__festController.getTickets()
        ticketsCountStr = backport.getIntegralFormat(ticketsCount)
        model.setTicketsStr(ticketsCountStr)

    def __updateItems(self, model):
        model.setReceivedItems(self.__festController.getReceivedItemsCount())
        model.setTotalItems(self.__festController.getTotalItemsCount())

    def __setContent(self, viewName, model):
        if viewName in _FESTIVAL_VIEW_CONTENTS:
            model.setContent(_FESTIVAL_VIEW_CONTENTS[viewName]())
        model.setCurrentView(viewName)
        self.__updateRndBuyHint(viewName)

    def __onAccountSettingsChanged(self, name, _):
        if name in (FESTIVAL_SHOP_VISITED, FESTIVAL_REWARDS_VISITED, FESTIVAL_INFO_VISITED):
            with self.viewModel.transaction() as model:
                self.__updateNotificationOnTab(model)

    def __updateNotificationOnTab(self, model):
        self.__contentNotificator.updateTabModel(model.getViews())

    def __updateRndBuyHint(self, viewName=None):
        if viewName is None:
            viewName = self.viewModel.getCurrentView()
        customizationCardView = self.viewModel.getCustomizationCardView()
        if customizationCardView is not None:
            customizationCardView.setFocus(viewName == FestivalViews.CARD)
        return
