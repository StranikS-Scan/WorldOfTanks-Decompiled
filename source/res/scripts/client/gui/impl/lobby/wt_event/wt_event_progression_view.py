# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_progression_view.py
import logging
import typing
from frameworks.wulf import ViewFlags, ViewSettings, ViewEvent
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_progression_view_model import WtProgressionViewModel
from gui.impl.lobby.wt_event import wt_event_sound
from gui.impl.lobby.wt_event.tooltips.wt_event_lootbox_tooltip_view import WtEventLootBoxTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_event_stamp_tooltip_view import WtEventStampTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_event_ticket_tooltip_view import WtEventTicketTooltipView
from gui.impl.lobby.wt_event.wt_progression_view import WTProgressionView
from gui.impl.lobby.wt_event.wt_quests_view import WTQuestsView
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.wt_event.wt_event_helpers import backportTooltipDecorator, getInfoPageURL
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IEventBattlesController
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Dict, List, Union
    from frameworks.wulf import View

class WTEventProgressionView(ViewImpl):
    __slots__ = ('questContainer', '__isGrowingAnimation', '__fromWelcome', '__ctx', '__subviews')
    __gameEventController = dependency.descriptor(IEventBattlesController)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WTEventProgression(), flags=ViewFlags.LOBBY_TOP_SUB_VIEW, model=WtProgressionViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WTEventProgressionView, self).__init__(settings)
        self.__isGrowingAnimation = False
        self.__fromWelcome = kwargs.get('fromWelcome', False)
        self.__ctx = kwargs.get('ctx', {})
        self.__subviews = []

    @property
    def viewModel(self):
        return super(WTEventProgressionView, self).getViewModel()

    @property
    def _tooltipItems(self):
        items = {}
        for subview in self.__subviews:
            subviewItems = subview.getTooltipItems()
            items.update(subviewItems)

        return items

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(WTEventProgressionView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.wt_event.tooltips.WtEventLootBoxTooltipView():
            return WtEventLootBoxTooltipView()
        if contentID == R.views.lobby.wt_event.tooltips.WtEventTicketTooltipView():
            return WtEventTicketTooltipView()
        return WtEventStampTooltipView() if contentID == R.views.lobby.wt_event.tooltips.WtEventStampTooltipView() else super(WTEventProgressionView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        for subview in self.__subviews:
            tooltipData = subview.getTooltipData(event)
            if tooltipData:
                return tooltipData

        return None

    def _onLoading(self, *args, **kwargs):
        if self.__fromWelcome:
            Waiting.show('loadContent')
        super(WTEventProgressionView, self)._onLoading()
        self.__subviews.append(WTProgressionView(self.viewModel, self))
        self.__subviews.append(WTQuestsView(self.viewModel.dailyQuests, self))
        for subview in self.__subviews:
            subview.initialize(**self.__ctx)

        self.__addListeners()

    def _onLoaded(self, *args, **kwargs):
        super(WTEventProgressionView, self)._onLoaded(*args, **kwargs)
        if self.__fromWelcome:
            Waiting.hide('loadContent')
        wt_event_sound.playProgressionViewEnter()
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        self.__removeListeners()
        for subview in self.__subviews:
            subview.finalize()
            subview.clear()

        self.__subviews = None
        wt_event_sound.playProgressionViewExit()
        if self.__isGrowingAnimation:
            wt_event_sound.playProgressBarGrowing(False)
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        super(WTEventProgressionView, self)._finalize()
        return

    @staticmethod
    def __onAboutClicked():
        showBrowserOverlayView(getInfoPageURL(), VIEW_ALIAS.BROWSER_OVERLAY)

    def __addListeners(self):
        self.viewModel.onClose += self.__onCloseHandler
        self.viewModel.onAboutClicked += self.__onAboutClicked
        self.__gameEventController.onEventPrbChanged += self.__onEventPrbChanged

    def __removeListeners(self):
        self.viewModel.onClose -= self.__onCloseHandler
        self.viewModel.onAboutClicked -= self.__onAboutClicked
        self.__gameEventController.onEventPrbChanged -= self.__onEventPrbChanged

    def __onEventPrbChanged(self, isActive):
        self.__checkAndCloseBrowserView()
        if not isActive:
            self.destroyWindow()

    def __checkAndCloseBrowserView(self):
        app = self.__appLoader.getApp()
        if app is None:
            return
        else:
            view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.BROWSER_OVERLAY))
            if view is None:
                return
            view.destroy()
            return

    def __onCloseHandler(self):
        self.__checkAndCloseBrowserView()
        self.destroyWindow()
