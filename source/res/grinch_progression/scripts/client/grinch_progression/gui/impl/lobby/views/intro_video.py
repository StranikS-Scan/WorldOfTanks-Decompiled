# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/lobby/views/intro_video.py
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer, ViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.pub.lobby_window import LobbyWindow

class IntroVideoView(ViewImpl):

    def __init__(self, layoutID=R.views.grinch_progression.lobby.IntroVideo(), *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.args = args
        settings.kwargs = kwargs
        settings.model = ViewModel()
        super(IntroVideoView, self).__init__(settings)


class IntroVideoWindow(LobbyWindow):

    def __init__(self):
        super(IntroVideoWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=IntroVideoView(), layer=WindowLayer.OVERLAY)
