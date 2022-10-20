# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/fade_manager.py
import logging
from functools import wraps
import typing
import BigWorld
import adisp
from wg_async import wg_await, wg_async
from frameworks.wulf import Window, View, WindowSettings, ViewSettings, WindowFlags, WindowStatus
from gui.impl.gen import R
from gui.impl.gen.view_models.common.fading_cover_view_model import FadingCoverViewModel
from gui.impl.gen_utils import DynAccessor
from gui.impl.pub.dialog_window import DialogWindow
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
    from typing import Callable, Optional, Union, Type
    from gui.Scaleform.framework.application import AppEntry
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper
_logger = logging.getLogger(__name__)
FADE_IN_DURATION = 0.15
FADE_OUT_DURATION = 0.4
VIEW_LOADING_DELAY = 0.1
BRING_TO_FRONT_FRAMES_COUNT = 2

class ICover(object):

    def fadeOut(self, onComplete):
        raise NotImplementedError

    def fadeIn(self, onComplete):
        raise NotImplementedError


class DefaultFadingCover(View, ICover):

    def __init__(self, background=None, fadeInDuration=FADE_IN_DURATION, fadeOutDuration=FADE_OUT_DURATION):
        model = FadingCoverViewModel()
        settings = ViewSettings(layoutID=R.views.common.FadingCoverView(), model=model)
        super(DefaultFadingCover, self).__init__(settings)
        self._onComplete = None
        model.setFadeInDuration(fadeInDuration)
        model.setFadeOutDuration(fadeOutDuration)
        if background:
            bgRes = background() if isinstance(background, DynAccessor) else background
            model.setBackground(bgRes)
        return

    @property
    def viewModel(self):
        return super(DefaultFadingCover, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(DefaultFadingCover, self)._onLoading(*args, **kwargs)
        self.viewModel.onFadingInComplete += self._fadingCompleteHandler
        self.viewModel.onFadingOutComplete += self._fadingCompleteHandler

    def _finalize(self):
        self.viewModel.onFadingInComplete -= self._fadingCompleteHandler
        self.viewModel.onFadingOutComplete -= self._fadingCompleteHandler
        if callable(self._onComplete):
            self._onComplete()
            self._onComplete = None
        super(DefaultFadingCover, self)._finalize()
        return

    def fadeOut(self, onComplete):
        self._onComplete = onComplete
        self.viewModel.setIsVisible(True)

    def fadeIn(self, onComplete):
        self._onComplete = onComplete
        self.viewModel.setIsVisible(False)

    def _fadingCompleteHandler(self):
        if callable(self._onComplete):
            cb = self._onComplete
            self._onComplete = None
            cb()
        return


class FadingCoverWindow(Window):

    def __init__(self, content, layer):
        settings = WindowSettings()
        settings.flags = WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN
        settings.layer = layer
        settings.content = content
        super(FadingCoverWindow, self).__init__(settings)

    @property
    def content(self):
        return super(FadingCoverWindow, self).content

    def fadeOut(self, onComplete):
        self.load()
        self.content.fadeOut(onComplete)

    def fadeIn(self, onComplete):
        self.content.fadeIn(onComplete)


class FadeManager(object):
    _gui = dependency.descriptor(IGuiLoader)
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, layer, coverFactory=None):
        super(FadeManager, self).__init__()
        self._layer = layer
        self._coverFactory = coverFactory
        self._currentWindow = None
        self._isDestroyed = False
        return

    def __enter__(self):
        return self

    def __exit__(self, exceptionType, exceptionValue, exceptionTraceBack):
        self.destroy()

    def destroy(self):
        self._gui.windowsManager.onWindowStatusChanged -= self._windowStatusChanged
        if self._currentWindow:
            self._currentWindow.destroy()
            self._currentWindow = None
        self._coverFactory = None
        self._isDestroyed = True
        return

    @property
    def isAnimating(self):
        return self._currentWindow is not None

    @adisp.adisp_async
    def show(self, callback=None):
        if self._isDestroyed:
            callback(None)
            return
        else:
            container = self._appLoader.getApp().containerManager.getContainer(self._layer)
            if not container:
                callback(None)
                return
            if self._currentWindow:
                raise SoftException("Can't show animation before previous one has been finished.")
            cover = self._coverFactory() if self._coverFactory else DefaultFadingCover()
            self._currentWindow = FadingCoverWindow(content=cover, layer=self._layer)
            self._currentWindow.fadeOut(lambda : callback(None))
            self._gui.windowsManager.onWindowStatusChanged += self._windowStatusChanged
            return

    @adisp.adisp_async
    def hide(self, callback=None):
        if self._isDestroyed:
            callback(None)
            return
        else:
            container = self._appLoader.getApp().containerManager.getContainer(self._layer)
            if not container or not self._currentWindow:
                callback(None)
                return

            def fadeInCompleteHandler():
                self._gui.windowsManager.onWindowStatusChanged -= self._windowStatusChanged
                if self._currentWindow:
                    self._currentWindow.destroy()
                    self._currentWindow = None
                callback(None)
                return

            self._currentWindow.fadeIn(fadeInCompleteHandler)
            return

    def _windowStatusChanged(self, uniqueID, newStatus):
        if not self.isAnimating:
            return
        if newStatus == WindowStatus.LOADING:
            window = self._gui.windowsManager.getWindow(uniqueID)
            if window == self._currentWindow or window.layer != self._currentWindow.layer:
                return
            BigWorld.callback(0.0, lambda : self._bringToFront(BRING_TO_FRONT_FRAMES_COUNT))

    def _bringToFront(self, framesLeft):
        if self._currentWindow:
            self._currentWindow.bringToFront()
            framesLeft -= 1
            if framesLeft > 0:
                BigWorld.callback(0.0, lambda : self._bringToFront(framesLeft))


class useFade(object):

    def __init__(self, layer, coverFactory, *args, **kwargs):
        super(useFade, self).__init__()
        self._layer = layer
        self._coverFactory = coverFactory
        self._args = args
        self._kwargs = kwargs

    def __call__(self, func):

        @wraps(func)
        @adisp.adisp_process
        def wrapper(*args, **kwargs):
            with FadeManager(self._layer, self._createCover) as fadeManager:
                yield wg_await(fadeManager.show())
                result = func(*args, **kwargs)
                if adisp.isAsync(func):
                    yield wg_await(result)
                yield wg_await(fadeManager.hide())

        return wrapper

    def _createCover(self):
        return self._coverFactory(*self._args, **self._kwargs)


class useDefaultFade(useFade):

    def __init__(self, layer, background=None, fadeInDuration=FADE_IN_DURATION, fadeOutDuration=FADE_OUT_DURATION):
        super(useDefaultFade, self).__init__(layer, DefaultFadingCover, background=background, fadeInDuration=fadeInDuration, fadeOutDuration=fadeOutDuration)


@adisp.adisp_async
def waitGuiImplViewLoading(loadParams, delay=None, callback=None, *args, **kwargs):
    if delay is None:
        delay = VIEW_LOADING_DELAY
    app = dependency.instance(IAppLoader).getApp()

    def viewLoadedHandler(view):
        if view.key.alias == loadParams.viewKey.alias:
            app.containerManager.onViewLoaded -= viewLoadedHandler
            BigWorld.callback(delay, lambda : callback(None))

    app.containerManager.onViewLoaded += viewLoadedHandler
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(loadParams, *args, **kwargs), scope=EVENT_BUS_SCOPE.LOBBY)
    return


@adisp.adisp_async
def waitWindowLoading(window, delay=None, callback=None):
    if delay is None:
        delay = VIEW_LOADING_DELAY

    def windowStatusChanged(newStatus):
        if newStatus in (WindowStatus.LOADED, WindowStatus.DESTROYING):
            window.onStatusChanged -= windowStatusChanged
            BigWorld.callback(delay, lambda : callback(None))

    window.onStatusChanged += windowStatusChanged
    window.load()
    return


@adisp.adisp_async
@wg_async
def showDialog(dialog, callback=None):
    result = yield wg_await(dialog.wait())
    callback(result)


@adisp.adisp_async
@adisp.adisp_process
def showDialogWithFading(dialog, layer=None, callback=None):
    with FadeManager(layer or dialog.layer) as fadeManager:
        yield wg_await(fadeManager.show())
        yield wg_await(waitWindowLoading(dialog))
        yield wg_await(fadeManager.hide())
        result = yield wg_await(showDialog(dialog))
        yield wg_await(fadeManager.show())
        dialog.destroy()
        yield wg_await(fadeManager.hide())
        callback(result)
