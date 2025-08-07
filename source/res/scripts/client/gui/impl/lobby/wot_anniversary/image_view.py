# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/image_view.py
import logging
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.image_view_model import ImageViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
_logger = logging.getLogger(__name__)

class ImageView(ViewImpl):

    def __init__(self, closeCallback=None, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wot_anniversary.ImageView(), model=ImageViewModel(), args=args, kwargs=kwargs)
        self.__closeCallback = closeCallback
        super(ImageView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    def _onLoading(self, imageSrc, *args, **kwargs):
        super(ImageView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setImageSrc(imageSrc)

    def _finalize(self):
        if self.__closeCallback is not None:
            self.__closeCallback()
            self.__closeCallback = None
        super(ImageView, self)._finalize()
        return

    def __onClose(self):
        self.destroyWindow()


class ImageWindow(LobbyWindow):

    def __init__(self, parent=None, *args, **kwargs):
        super(ImageWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=ImageView(*args, **kwargs), parent=parent)
