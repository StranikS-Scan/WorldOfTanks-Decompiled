# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bootcamp/bootcamp_progress_view.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.impl.gen.view_models.views.bootcamp.bootcamp_progress_model import BootcampProgressModel
from uilogging.deprecated.bootcamp.constants import BC_LOG_KEYS, BC_LOG_ACTIONS
from uilogging.deprecated.bootcamp.loggers import BootcampLogger
from gui.impl.lobby.bootcamp.bootcamp_progress_base_view import BootcampProgressBaseView

class BootcampProgressView(BootcampProgressBaseView):
    __slots__ = ('__blur',)
    uiBootcampLogger = BootcampLogger(BC_LOG_KEYS.BC_CURRENT_PROGRESS_WIDGET)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = BootcampProgressModel()
        settings.args = args
        settings.kwargs = kwargs
        super(BootcampProgressView, self).__init__(settings)
        self.__blur = None
        return

    def _initialize(self):
        super(BootcampProgressView, self)._initialize()
        window = self.getParentWindow()
        self.__blur = CachedBlur(enabled=True, ownLayer=window.layer - 1)

    def _finalize(self):
        self.uiBootcampLogger.log(BC_LOG_ACTIONS.CLOSE)
        self.__blur.fini()
        super(BootcampProgressView, self)._finalize()


class BootcampProgressWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, wndFlags=None):
        if wndFlags is None:
            wndFlags = WindowFlags.SERVICE_WINDOW | WindowFlags.WINDOW_FULLSCREEN
        super(BootcampProgressWindow, self).__init__(content=BootcampProgressView(R.views.lobby.bootcamp.BootcampProgressView()), wndFlags=wndFlags)
        return
