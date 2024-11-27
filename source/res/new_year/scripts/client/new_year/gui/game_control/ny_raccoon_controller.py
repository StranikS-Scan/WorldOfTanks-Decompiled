# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/game_control/ny_raccoon_controller.py
import Event
from frameworks.wulf import WindowLayer
from gui.impl.common.fade_manager import DefaultFadingCover, FadeManager
from helpers import dependency
from new_year.skeletons.new_year import INewYearRaccoonController
from wg_async import wg_await, wg_async
_FADE_IN_DURATION = 0.15
_FADE_OUT_DURATION = 0.15

class NYFadingCover(DefaultFadingCover):
    __raccoonCtrl = dependency.descriptor(INewYearRaccoonController)

    def __init__(self):
        super(NYFadingCover, self).__init__(fadeInDuration=_FADE_IN_DURATION, fadeOutDuration=_FADE_OUT_DURATION)

    def fadeOut(self, _):
        super(NYFadingCover, self).fadeOut(self.__onComplete)

    def __onComplete(self):
        self.__raccoonCtrl.hideFade()


class NewYearRaccoonController(INewYearRaccoonController):
    __slots__ = ('__fadeManager', '__isFade', '__callback')

    def __init__(self):
        self.onViewExit = Event.Event()
        self.__fadeManager = FadeManager(layer=WindowLayer.TOP_WINDOW, coverFactory=NYFadingCover)
        self.__isFade = False
        self.__callback = None
        return

    def fini(self):
        self.__fadeManager.destroy()

    @wg_async
    def showFade(self, callback=None):
        self.__callback = callback
        if not self.__isFade:
            self.__isFade = True
            yield wg_await(self.__fadeManager.show())

    @wg_async
    def hideFade(self):
        if self.__callback:
            self.__callback()
        if self.__isFade:
            yield wg_await(self.__fadeManager.hide())
            self.__fadeManager.hideImmediately()
            self.__isFade = False
