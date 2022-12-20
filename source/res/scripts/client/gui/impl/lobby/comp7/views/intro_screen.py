# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/views/intro_screen.py
import logging
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import GUI_START_BEHAVIOR
from account_helpers.settings_core.settings_constants import GuiSettingsBehavior
from frameworks.wulf import ViewSettings, ViewFlags, WindowFlags, WindowLayer
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.views.intro_screen_model import IntroScreenModel
from gui.impl.lobby.comp7 import comp7_model_helpers
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import event_dispatcher
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IComp7Controller
_logger = logging.getLogger(__name__)

class IntroScreen(ViewImpl, IGlobalListener):
    __slots__ = ()
    __settingsCore = dependency.descriptor(ISettingsCore)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
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
        self.__setComp7IntroShown()

    def __addListeners(self):
        self.viewModel.onClose += self.__onClose
        self.viewModel.scheduleInfo.season.pollServerTime += self.__onPollServerTime
        self.__comp7Controller.onStatusUpdated += self.__onStatusUpdated
        self.startGlobalListening()

    def __removeListeners(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.scheduleInfo.season.pollServerTime -= self.__onPollServerTime
        self.__comp7Controller.onStatusUpdated -= self.__onStatusUpdated
        self.stopGlobalListening()

    def __onStatusUpdated(self, status):
        if comp7_model_helpers.isModeForcedDisabled(status):
            self.destroyWindow()
        else:
            self.__updateData()

    def __updateData(self):
        with self.viewModel.transaction() as vm:
            comp7_model_helpers.setScheduleInfo(vm.scheduleInfo)

    def __setComp7IntroShown(self):
        if not self.__settingsCore.isReady:
            _logger.error('Can not save Comp7IntroShown settings: settings are not ready')
            return
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        stateFlags = self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        stateFlags[GuiSettingsBehavior.COMP7_INTRO_SHOWN] = True
        self.__settingsCore.serverSettings.setSectionSettings(GUI_START_BEHAVIOR, stateFlags)

    def __onClose(self):
        event_dispatcher.showHangar()
        self.destroyWindow()

    def __onPollServerTime(self):
        self.__updateData()


class IntroScreenWindow(LobbyWindow):

    def __init__(self, parent=None):
        super(IntroScreenWindow, self).__init__(wndFlags=WindowFlags.WINDOW, content=IntroScreen(layoutID=R.views.lobby.comp7.views.IntroScreen()), parent=parent, layer=WindowLayer.TOP_SUB_VIEW)
