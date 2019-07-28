# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/managers/fade_manager.py
import math
import GUI
from adisp import async
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
_FADE_WINDOW_PATH = 'gui/flash/fadeWindow.swf'

class FadeManager(CallbackDelayer, TimeDeltaMeter):
    FADE_TIME = 0.6
    FADE_IN_ALPHA = 1.0
    MAX_DT = 0.02
    CALLBACK_TIME = 0.5

    def __init__(self):
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self.__fadeInCallback = None
        self.__fadeInTime = None
        self.__fadeWindow = None
        return

    def setup(self):
        self.__fadeWindow = _FadeWindow()

    def destroy(self):
        if self.__fadeInCallback:
            self.__fadeInCallback(False)
        self.__fadeWindow.deactivate()
        self.__fadeWindow = None
        super(FadeManager, self).destroy()
        return

    def isInFade(self):
        return self.__fadeInTime is not None

    @async
    def startFade(self, callback):
        if not self.isInFade():
            self.__fadeInCallback = callback
            self.__fadeWindow.activate()
            self.__fadeWindow.setAlpha(0.0)
            self.__fadeInTime = 0.0
            self.measureDeltaTime()
            self.delayCallback(0.0, self.__inFadeUpdate)
        else:
            callback(self.__fadeInTime >= self.CALLBACK_TIME)

    def __inFadeUpdate(self):
        self.__fadeInTime += min(self.measureDeltaTime(), self.MAX_DT) / self.FADE_TIME
        if self.__fadeInTime >= self.CALLBACK_TIME:
            if self.__fadeInCallback:
                self.__fadeInCallback(True)
                self.__fadeInCallback = None
        k = math.sin(self.__fadeInTime * math.pi)
        alpha = min(k * self.FADE_IN_ALPHA, 1.0)
        self.__fadeWindow.setAlpha(alpha)
        if self.__fadeInTime < 1.0:
            return 0.0
        else:
            self.__fadeInTime = None
            self.__fadeWindow.deactivate()
            return


class _FadeWindow(object):

    def __init__(self):
        self.__component = GUI.Flash(_FADE_WINDOW_PATH, 0)
        self.__component.position.z = 0.1
        self.__component.size = (2, 2)
        self.__component.focus = True
        self.__component.moveFocus = True
        self.__component.wg_inputKeyMode = 2

    def activate(self):
        GUI.addRoot(self.__component)
        GUI.reSort()

    def deactivate(self):
        GUI.delRoot(self.__component)

    def setAlpha(self, alpha):
        self.__component.movie.backgroundAlpha = alpha
