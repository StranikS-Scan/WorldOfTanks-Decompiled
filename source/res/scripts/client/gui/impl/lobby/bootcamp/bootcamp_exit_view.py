# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bootcamp/bootcamp_exit_view.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.bootcamp.bootcamp_exit_model import BootcampExitModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared import g_eventBus, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from bootcamp.Bootcamp import g_bootcamp
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IBootcampController
from uilogging.bootcamp.constants import BCLogKeys, BCLogActions
from uilogging.bootcamp.loggers import BootcampLogger

class BootcampExitView(ViewImpl):
    __slots__ = ('__blur', '__tooltipData', '__callback', '__isInBattle')
    __appLoader = dependency.descriptor(IAppLoader)
    __bootcampController = dependency.descriptor(IBootcampController)
    uiBootcampLogger = BootcampLogger(BCLogKeys.BC_EXIT_VIEW.value)

    def __init__(self, callback, isInBattle, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.bootcamp.BootcampExitView())
        settings.model = BootcampExitModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__blur = None
        self.__tooltipData = {}
        self.__callback = callback
        self.__isInBattle = isInBattle
        super(BootcampExitView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BootcampExitView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId:
                tooltipData = self.__tooltipData[int(tooltipId)]
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                if window is None:
                    return
                window.load()
                return window
        return

    def _initialize(self):
        super(BootcampExitView, self)._initialize()
        window = self.getParentWindow()
        if self.__isInBattle:
            app = self.__appLoader.getApp()
            app.enterGuiControlMode(self.uniqueID, True, False)
        else:
            self.__blur = CachedBlur(enabled=True, ownLayer=window.layer - 1)

    @uiBootcampLogger.dLog(BCLogActions.SHOW.value)
    def _onLoading(self, *args, **kwargs):
        super(BootcampExitView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.onLeaveBootcamp += self.__onLeave
            model.setIsInBattle(self.__isInBattle)
            model.setIsNeedAwarding(self.__bootcampController.needAwarding())
            model.setIsReferral(self.__bootcampController.isReferralEnabled())
            g_bootcamp.fillProgressBar(model, self.__tooltipData)

    @uiBootcampLogger.dLog(BCLogActions.CLOSE.value)
    def _finalize(self):
        self.viewModel.onLeaveBootcamp -= self.__onLeave
        if self.__isInBattle:
            app = self.__appLoader.getApp()
            app.leaveGuiControlMode(self.uniqueID)
        g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__blur:
            self.__blur.fini()
        super(BootcampExitView, self)._finalize()

    @uiBootcampLogger.dLog(BCLogActions.LEAVE.value)
    def __onLeave(self):
        self.__callback()
        self.destroyWindow()


class BootcampExitWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, callback, isInBattle=False):
        super(BootcampExitWindow, self).__init__(content=BootcampExitView(callback, isInBattle), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN)
