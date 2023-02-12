# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bootcamp/bootcamp_exit_view.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.bootcamp.bootcamp_exit_model import BootcampExitModel
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared import g_eventBus, events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from uilogging.deprecated.bootcamp.constants import BC_LOG_KEYS, BC_LOG_ACTIONS
from uilogging.deprecated.bootcamp.loggers import BootcampLogger
from gui.impl.lobby.bootcamp.bootcamp_progress_base_view import BootcampProgressBaseView

class BootcampExitView(BootcampProgressBaseView):
    __slots__ = ('__blur', '__onQuit', '__onCancel', '__isInBattle')
    __appLoader = dependency.descriptor(IAppLoader)
    uiBootcampLogger = BootcampLogger(BC_LOG_KEYS.BC_EXIT_VIEW)

    def __init__(self, onQuit, isInBattle, onCancel=None, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.bootcamp.BootcampExitView())
        settings.model = BootcampExitModel()
        settings.args = args
        settings.kwargs = kwargs
        super(BootcampExitView, self).__init__(settings)
        self.__blur = None
        self.__onQuit = onQuit
        self.__onCancel = onCancel
        self.__isInBattle = isInBattle
        return

    def _initialize(self):
        super(BootcampExitView, self)._initialize()
        window = self.getParentWindow()
        if self.__isInBattle:
            app = self.__appLoader.getApp()
            app.enterGuiControlMode(self.uniqueID, True, False)
        else:
            self.__blur = CachedBlur(enabled=True, ownLayer=window.layer - 1)

    def _setupModel(self, model):
        super(BootcampExitView, self)._setupModel(model)
        model.onLeaveBootcamp += self.__onLeave
        model.setIsInBattle(self.__isInBattle)
        model.setIsReferral(self.bootcampController.isReferralEnabled())

    def _onLoading(self, *args, **kwargs):
        super(BootcampExitView, self)._onLoading(*args, **kwargs)
        self.uiBootcampLogger.log(BC_LOG_ACTIONS.SHOW)

    def _finalize(self):
        self.uiBootcampLogger.log(BC_LOG_ACTIONS.CLOSE)
        self.viewModel.onLeaveBootcamp -= self.__onLeave
        if self.__isInBattle:
            app = self.__appLoader.getApp()
            app.leaveGuiControlMode(self.uniqueID)
        if self.bootcampController.isInBootcamp():
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__blur:
            self.__blur.fini()
        if callable(self.__onCancel):
            self.__onCancel()
        super(BootcampExitView, self)._finalize()

    def __onLeave(self):
        self.uiBootcampLogger.log(BC_LOG_ACTIONS.LEAVE)
        self.__onCancel = None
        self.__onQuit()
        self.destroyWindow()
        return


class BootcampExitWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, onQuit, isInBattle=False, onCancel=None):
        super(BootcampExitWindow, self).__init__(content=BootcampExitView(onQuit, isInBattle, onCancel), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN)
