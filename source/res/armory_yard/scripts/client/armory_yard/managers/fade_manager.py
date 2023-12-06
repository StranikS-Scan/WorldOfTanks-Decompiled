# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/managers/fade_manager.py
import math
import Event
import GUI
from adisp import adisp_async
from enumerations import Enumeration
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
_FADE_WINDOW_PATH = 'gui/flash/animations/fadeWindow/fadeWindow.swf'
ArmoryYardFadeState = Enumeration('ArmoryYardFadeState', ['released', 'refused', 'destroying'])

class ArmoryYardFadeManager(CallbackDelayer, TimeDeltaMeter):
    FADE_TIME = 0.3
    FADE_IN_ALPHA = 1.0
    MAX_DT = 0.02
    CALLBACK_TIME = 0.3

    def __init__(self):
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self.onFadeUpdated = Event.Event()
        self.__fadeInCallback = None
        self.__fadeInTime = None
        self.__fadeWindow = None
        self.__isFadeIn = True
        return

    def setup(self):
        self.__fadeWindow = _FadeWindow()

    def destroy(self):
        if self.__fadeInCallback:
            self.__fadeInCallback(ArmoryYardFadeState.destroying)
        self.__fadeWindow.deactivate()
        self.__fadeWindow = None
        super(ArmoryYardFadeManager, self).destroy()
        return

    def isActive(self):
        return self.__fadeWindow is not None

    @adisp_async
    def startFade(self, callback, fadeIn=True):
        if not self.isInFade():
            self.__fadeInCallback = callback
            self.__fadeWindow.activate()
            if fadeIn:
                self.__fadeWindow.setAlpha(0.0)
            else:
                self.__fadeWindow.setAlpha(1.0)
            self.__fadeInTime = 0.0
        else:
            callback(ArmoryYardFadeState.refused)
            return
        self.__isFadeIn = fadeIn
        self.onFadeUpdated(True)
        self.measureDeltaTime()
        self.delayCallback(0.0, self.__inFadeUpdate)

    def isInFade(self):
        return self.__fadeInTime is not None

    def __inFadeUpdate(self):
        self.__fadeInTime += min(self.measureDeltaTime(), self.MAX_DT) / self.FADE_TIME
        if self.__fadeInTime >= self.CALLBACK_TIME and self.__fadeInCallback:
            self.__fadeInCallback(ArmoryYardFadeState.released)
            self.onFadeUpdated(False)
            self.__fadeInCallback = None
        if self.__isFadeIn:
            k = math.sin(self.__fadeInTime * math.pi / 2.0)
        else:
            k = math.cos(self.__fadeInTime * math.pi / 2.0)
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
        self.__component = GUI.Flash(_FADE_WINDOW_PATH)
        self.__component.size = (2, 2)
        self.__component.focus = True
        self.__component.moveFocus = True
        self.__component.wg_inputKeyMode = 2
        self.__activated = False

    def activate(self):
        if not self.__activated:
            GUI.addRoot(self.__component)
            GUI.reSort()
            self.__activated = True

    def deactivate(self):
        if self.__activated:
            GUI.delRoot(self.__component)
            self.__activated = False

    def setAlpha(self, alpha):
        self.__component.movie.backgroundAlpha = alpha
