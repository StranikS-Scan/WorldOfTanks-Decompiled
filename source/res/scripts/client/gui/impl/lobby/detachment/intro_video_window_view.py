# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/intro_video_window_view.py
import logging
from Event import Event
from async import async, AsyncScope, AsyncEvent, BrokenPromiseError, AsyncReturn, await
from gui.battle_pass.sounds import AwardVideoSoundControl
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.dialogs import SingleDialogResult
from gui.impl.gen import R
from gui.impl.lobby.video.video_view import VideoView
from gui.impl.pub.dialog_window import DialogFlags, DialogButtons
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.view_helpers.blur_manager import CachedBlur
_logger = logging.getLogger(__name__)

class DetachmentIntroVideoView(VideoView):
    __slots__ = ('__withClosingDialog', 'onQuitDialogShown', 'onQuitDialogHidden', '__event', '__scope')

    def __init__(self, *args, **kwargs):
        layoutID = R.views.lobby.detachment.detachment_video_view.DetachmentVideoView()
        super(DetachmentIntroVideoView, self).__init__(layoutID, *args, **kwargs)
        self.__withClosingDialog = kwargs.get('withClosingDialog', False)
        self.onQuitDialogShown = Event()
        self.onQuitDialogHidden = Event()
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)

    def destroyWindow(self):
        self.__event.set()

    @async
    def wait(self):
        try:
            yield await(self.__event.wait())
        except BrokenPromiseError:
            _logger.debug('%s has been destroyed without user decision', self)

        raise AsyncReturn(SingleDialogResult(busy=False, result=DialogButtons.SUBMIT))

    def _onCloseWindow(self, *args, **kwargs):
        if self.__withClosingDialog:
            self.__showDialog()
        else:
            super(DetachmentIntroVideoView, self)._onCloseWindow(*args, **kwargs)

    def _finalize(self):
        self.__scope.destroy()
        super(DetachmentIntroVideoView, self)._finalize()

    @async
    def __showDialog(self):
        if self.isPaused:
            return
        self.isPaused = True
        self.onQuitDialogShown()
        doQuit = yield await(dialogs.showCloseIntroVideoDialogView())
        self.onQuitDialogHidden()
        if doQuit:
            self.destroyWindow()
        else:
            self.isPaused = False


class DetachmentIntroVideoWindow(LobbyWindow):
    __slots__ = ('__blur',)

    def __init__(self, *args, **kwargs):
        videoSource = R.videos.detachment.intro()
        kwargs.update({'videoSource': videoSource,
         'isAutoClose': True,
         'soundControl': AwardVideoSoundControl(R.videos.battle_pass.c_67404_4())})
        super(DetachmentIntroVideoWindow, self).__init__(wndFlags=DialogFlags.TOP_FULLSCREEN_WINDOW, content=DetachmentIntroVideoView(*args, **kwargs))
        self.__blur = CachedBlur(ownLayer=self.layer)
        self.content.onQuitDialogShown += self.__blur.enable
        self.content.onQuitDialogHidden += self.__blur.disable

    def wait(self):
        return self.content.wait()

    def _finalize(self):
        self.__blur.fini()
        self.content.onQuitDialogShown -= self.__blur.enable
        self.content.onQuitDialogHidden -= self.__blur.disable
        self.__blur = None
        super(DetachmentIntroVideoWindow, self)._finalize()
        return
