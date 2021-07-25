# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/convert_info_window_view.py
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen.view_models.views.lobby.detachment.convert_window_model import ConvertWindowModel
from gui.impl.pub.dialog_window import DialogFlags
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.gen import R
from uilogging.detachment.loggers import DetachmentLogger
from uilogging.detachment.constants import ACTION, GROUP

class ConvertInfoWindowView(ViewImpl):
    uiLogger = DetachmentLogger(GROUP.MOBILIZE_CREW_INFO)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.model = ConvertWindowModel()
        super(ConvertInfoWindowView, self).__init__(settings)

    @uiLogger.dStartAction(ACTION.OPEN)
    def _initialize(self, *args, **kwargs):
        super(ConvertInfoWindowView, self)._initialize()

    @uiLogger.dStopAction(ACTION.OPEN)
    def _finalize(self):
        super(ConvertInfoWindowView, self)._finalize()


class ConvertInfoWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(ConvertInfoWindow, self).__init__(DialogFlags.TOP_FULLSCREEN_WINDOW, content=ConvertInfoWindowView(R.views.lobby.detachment.ConvertInfoWindow()), parent=parent)
