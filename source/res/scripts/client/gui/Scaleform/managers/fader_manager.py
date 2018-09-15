# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/managers/fader_manager.py
import math
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import FaderEvent
from new_year.fade_window import FadeWindow

class FaderManager(CallbackDelayer, TimeDeltaMeter):
    FADE_TIME = 0.6
    FADE_IN_ALPHA = 1.0
    MAX_DT = 0.02
    CALLBACK_TIME = 0.5

    def __init__(self):
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self.__fadeInCallbacks = []
        self.__fadeInTime = None
        self.__events = None
        self.__fadeWindow = None
        return

    def setup(self):
        self.__events = set()
        self.__fadeWindow = FadeWindow()

    def destroy(self):
        self.__doCallbacks()
        self.__fadeWindow.deactivate()
        self.__fadeWindow = None
        for event in self.__events:
            event -= self.startFade

        self.__events.clear()
        super(FaderManager, self).destroy()
        return

    def isInFade(self):
        return self.__fadeInTime is not None

    def addFadeEvent(self, event):
        self.__events.add(event)
        event += self.startFade

    def startFade(self, callbacks=None):
        self.__fadeInCallbacks.extend(callbacks or [])
        if not self.isInFade():
            self.__fadeWindow.activate()
            self.__fadeWindow.setAlpha(0.0)
            self.__fadeInTime = 0.0
            self.measureDeltaTime()
            self.delayCallback(0.0, self.__inFadeUpdate)
            g_eventBus.handleEvent(FaderEvent(FaderEvent.FADE_IN), EVENT_BUS_SCOPE.LOBBY)

    def __inFadeUpdate(self):
        self.__fadeInTime += min(self.measureDeltaTime(), self.MAX_DT) / self.FADE_TIME
        if self.__fadeInTime >= self.CALLBACK_TIME:
            self.__doCallbacks()
        k = math.sin(self.__fadeInTime * math.pi)
        alpha = min(k * self.FADE_IN_ALPHA, 1.0)
        self.__fadeWindow.setAlpha(alpha)
        if self.__fadeInTime < 1.0:
            return 0.0
        else:
            self.__fadeInTime = None
            self.__fadeWindow.deactivate()
            g_eventBus.handleEvent(FaderEvent(FaderEvent.FADE_OUT), EVENT_BUS_SCOPE.LOBBY)
            return

    def __doCallbacks(self):
        while self.__fadeInCallbacks:
            clb = self.__fadeInCallbacks.pop(0)
            if clb is not None:
                clb()

        return
