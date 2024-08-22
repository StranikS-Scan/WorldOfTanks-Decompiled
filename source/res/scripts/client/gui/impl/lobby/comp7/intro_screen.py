# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/intro_screen.py
import logging
import typing
from frameworks.wulf import ViewSettings, ViewFlags, WindowFlags
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.intro_screen_model import IntroScreenModel
from gui.impl.lobby.comp7 import comp7_model_helpers
from gui.impl.lobby.comp7.comp7_gui_helpers import updateComp7LastSeason
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import event_dispatcher
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IComp7Controller
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
_logger = logging.getLogger(__name__)

class IntroScreen(ViewImpl, IGlobalListener):
    __slots__ = ()
    __settingsCore = dependency.descriptor(ISettingsCore)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = IntroScreenModel()
        super(IntroScreen, self).__init__(settings)

    @property
    def viewModel(self):
        return super(IntroScreen, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            tooltipData = None
            if tooltipId == TOOLTIPS_CONSTANTS.COMP7_CALENDAR_DAY_INFO:
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=(None,))
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(IntroScreen, self).createToolTip(event)

    def onPrbEntitySwitched(self):
        if not self.__comp7Controller.isComp7PrbActive():
            self.destroyWindow()

    def _finalize(self):
        self.__removeListeners()

    def _onLoading(self, *_, **__):
        self.__addListeners()
        self.__updateData()

    def _onLoaded(self):
        updateComp7LastSeason()

    def __addListeners(self):
        self.viewModel.onClose += self.__onClose
        self.viewModel.scheduleInfo.season.pollServerTime += self.__onPollServerTime
        self.__comp7Controller.onStatusUpdated += self.__onStatusUpdated
        self.startGlobalListening()
        g_eventBus.addListener(events.LobbyHeaderMenuEvent.MENU_CLICK, self.__onHeaderMenuClick, scope=EVENT_BUS_SCOPE.LOBBY)

    def __removeListeners(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.scheduleInfo.season.pollServerTime -= self.__onPollServerTime
        self.__comp7Controller.onStatusUpdated -= self.__onStatusUpdated
        self.stopGlobalListening()
        g_eventBus.removeListener(events.LobbyHeaderMenuEvent.MENU_CLICK, self.__onHeaderMenuClick, scope=EVENT_BUS_SCOPE.LOBBY)

    def __onStatusUpdated(self, status):
        if comp7_model_helpers.isModeForcedDisabled(status):
            self.destroyWindow()
        else:
            self.__updateData()

    def __updateData(self):
        with self.viewModel.transaction() as vm:
            comp7_model_helpers.setScheduleInfo(vm.scheduleInfo)
            vm.setQualificationBattlesCount(self.__comp7Controller.qualificationBattlesNumber)

    def __onClose(self):
        event_dispatcher.showHangar()
        self.destroyWindow()

    def __onPollServerTime(self):
        self.__updateData()

    def __onHeaderMenuClick(self, *_):
        self.destroyWindow()


class IntroScreenWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(IntroScreenWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=IntroScreen(R.views.lobby.comp7.IntroScreen()), parent=parent)
