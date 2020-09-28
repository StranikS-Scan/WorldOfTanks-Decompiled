# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_header_widget_view.py
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import WT_EVENT_LAST_COLLECTION_SEEN
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.WhiteTigerWidgetMeta import WhiteTigerWidgetMeta
from gui.shared.event_dispatcher import showWtEventCollectionWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_header_widget_view_model import WtEventHeaderWidgetViewModel
from gui.impl.lobby.wt_event.tooltips.wt_event_header_widget_tooltip_view import WtEventHeaderWidgetTooltipView
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IGameEventController

class WtEventWidgetStates(object):

    def __init__(self):
        self.isFirstShow = True
        g_playerEvents.onDisconnected += self.reset
        g_playerEvents.onAccountBecomePlayer += self.reset

    def __del__(self):
        g_playerEvents.onDisconnected -= self.reset
        g_playerEvents.onAccountBecomePlayer -= self.reset

    def reset(self):
        self.isFirstShow = True


g_WtEventWidgetStates = WtEventWidgetStates()

class WTEventHeaderWidgetComponent(WhiteTigerWidgetMeta):
    __slots__ = ('__view', '__isSmall')

    def __init__(self):
        super(WTEventHeaderWidgetComponent, self).__init__()
        self.__isSmall = False

    def setIsSmall(self, value):
        self.__isSmall = value
        if self.__view is not None:
            self.__view.setIsSmall(self.__isSmall)
        return

    def _dispose(self):
        self.__view = None
        super(WTEventHeaderWidgetComponent, self)._dispose()
        return

    def _makeInjectView(self):
        self.__view = WTEventHeaderWidgetView(self.as_setIsMouseEnabledS, flags=ViewFlags.COMPONENT)
        self.__view.setIsSmall(self.__isSmall)
        return self.__view


class WTEventHeaderWidgetView(ViewImpl):
    __slots__ = ('__setIsMouseEnabled', '__isSmall')
    __eventController = dependency.descriptor(IGameEventController)

    def __init__(self, setIsMouseEnabled, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.wt_event.WTEventHeaderWidget())
        settings.flags = flags
        settings.model = WtEventHeaderWidgetViewModel()
        self.__setIsMouseEnabled = setIsMouseEnabled
        self.__isSmall = False
        super(WTEventHeaderWidgetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WTEventHeaderWidgetView, self).getViewModel()

    def setIsSmall(self, value):
        if self.viewModel.proxy:
            self.viewModel.setIsSmall(value)
        self.__isSmall = value

    def createToolTipContent(self, event, contentID):
        return WtEventHeaderWidgetTooltipView()

    def _onLoading(self, *args, **kwargs):
        super(WTEventHeaderWidgetView, self)._onLoading(*args, **kwargs)
        self.__addListeners()
        self.__updateViewModel()

    def _finalize(self):
        self.__removeListeners()
        self.__setIsMouseEnabled = None
        super(WTEventHeaderWidgetView, self)._finalize()
        return

    def __addListeners(self):
        self.viewModel.onClick += self.__onClick
        self.__eventController.onProgressUpdated += self.__onProgressUpdated
        AccountSettings.onSettingsChanging += self.__onAccountSettingsChanging

    def __removeListeners(self):
        self.viewModel.onClick -= self.__onClick
        self.__eventController.onProgressUpdated -= self.__onProgressUpdated
        AccountSettings.onSettingsChanging -= self.__onAccountSettingsChanging

    def __onProgressUpdated(self):
        self.__updateViewModel()

    def __onAccountSettingsChanging(self, key, _):
        if key == WT_EVENT_LAST_COLLECTION_SEEN:
            self.__updateIsNewItems()

    def __onClick(self):
        showWtEventCollectionWindow()

    def __updateViewModel(self):
        self.__setIsMouseEnabled(True)
        tooltip = R.views.lobby.wt_event.tooltips.WtEventHeaderWidgetTooltipView()
        currentProgress = self.__eventController.getTotalCollectedCount()
        totalProgress = self.__eventController.getTotalCollectionSize()
        with self.getViewModel().transaction() as model:
            model.setIsSmall(self.__isSmall)
            model.setTooltipID(tooltip)
            model.setAllCollected(currentProgress == totalProgress)
            model.setIsFirstShow(g_WtEventWidgetStates.isFirstShow)
            self.__updateIsNewItems()
        g_WtEventWidgetStates.isFirstShow = False

    def __updateIsNewItems(self):
        with self.viewModel.transaction() as model:
            previous = AccountSettings.getSettings(WT_EVENT_LAST_COLLECTION_SEEN)
            current = self.__eventController.getHunterCollectedCount() + self.__eventController.getBossCollectedCount()
            model.setIsNewItem(current > previous)
