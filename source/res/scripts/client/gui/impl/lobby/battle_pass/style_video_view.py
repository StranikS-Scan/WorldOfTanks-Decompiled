# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/style_video_view.py
import logging
import BigWorld
import SoundGroups
import Windowing
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.style_video_view_model import StyleVideoViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.sounds.filters import switchVideoOverlaySoundFilter
_logger = logging.getLogger(__name__)

class StyleVideoView(ViewImpl):
    __slots__ = ('__onVideoClosedHandle',)
    __appFactory = dependency.descriptor(IAppLoader)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = StyleVideoViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(StyleVideoView, self).__init__(settings)
        self.__onVideoClosedHandle = kwargs.get('onVideoClosed')

    @property
    def viewModel(self):
        return super(StyleVideoView, self).getViewModel()

    def onClose(self):
        self.destroyWindow()

    def _onLoading(self, chapter, level, *args, **kwargs):
        super(StyleVideoView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setChapter(chapter)
            model.setLevel(level)
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)
        switchVideoOverlaySoundFilter(on=True)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.onClose),)

    def _initialize(self, *args, **kwargs):
        super(StyleVideoView, self)._initialize(*args, **kwargs)
        self.__hideBack()

    def _finalize(self):
        self.__showBack()
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        if callable(self.__onVideoClosedHandle):
            self.__onVideoClosedHandle()
            self.__onVideoClosedHandle = None
        SoundGroups.g_instance.playSound2D(BattlePassSounds.VIDEO_STOP)
        switchVideoOverlaySoundFilter(on=False)
        return

    def __hideBack(self):
        BigWorld.worldDrawEnabled(False)

    def __showBack(self):
        BigWorld.worldDrawEnabled(True)

    def __onWindowAccessibilityChanged(self, _):
        isWindowAccessible = Windowing.isWindowAccessible()
        if isWindowAccessible:
            SoundGroups.g_instance.playSound2D(BattlePassSounds.VIDEO_RESUME)
        else:
            SoundGroups.g_instance.playSound2D(BattlePassSounds.VIDEO_PAUSE)


class StyleVideoViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(StyleVideoViewWindow, self).__init__(content=StyleVideoView(R.views.lobby.battle_pass.StyleVideoView(), *args, **kwargs), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW)
