# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bootcamp/bootcamp_progress_view.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.view_helpers.blur_manager import CachedBlur
from bootcamp.Bootcamp import g_bootcamp, ICON_SIZE
from gui.impl.gen.view_models.views.bootcamp.bootcamp_progress_model import BootcampProgressModel

class BootcampProgressView(ViewImpl):
    __slots__ = ('__blur', '__tooltipData')

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = BootcampProgressModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__blur = None
        self.__tooltipData = {}
        super(BootcampProgressView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BootcampProgressView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId:
                tooltipData = self.__tooltipData[int(tooltipId)]
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                if window:
                    window.load()
                return window

    def _initialize(self):
        super(BootcampProgressView, self)._initialize()
        window = self.getParentWindow()
        self.__blur = CachedBlur(enabled=True, ownLayer=window.layer - 1)

    def _onLoading(self, *args, **kwargs):
        super(BootcampProgressView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            g_bootcamp.fillProgressBar(model, self.__tooltipData, ICON_SIZE.BIG)

    def _finalize(self):
        self.__blur.fini()
        super(BootcampProgressView, self)._finalize()


class BootcampProgressWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, wndFlags=None):
        if wndFlags is None:
            wndFlags = WindowFlags.SERVICE_WINDOW | WindowFlags.WINDOW_FULLSCREEN
        super(BootcampProgressWindow, self).__init__(content=BootcampProgressView(R.views.lobby.bootcamp.BootcampProgressView()), wndFlags=wndFlags)
        return
