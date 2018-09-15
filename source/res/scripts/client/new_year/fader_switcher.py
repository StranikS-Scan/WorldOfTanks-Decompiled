# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/fader_switcher.py
import Event
from functools import partial
from gui.app_loader.decorators import sf_lobby
from gui.shared.utils.HangarSpace import g_hangarSpace
from .abstract_switch_handler import AbstractSwitchHandler

class FaderSwitcher(AbstractSwitchHandler):

    def __init__(self):
        super(FaderSwitcher, self).__init__()
        self.onSwitchEvent = Event.Event()
        g_hangarSpace.onSpaceCreate += self.__initFader

    def fini(self):
        g_hangarSpace.onSpaceCreate -= self.__initFader
        super(FaderSwitcher, self).fini()

    def switchTo(self, state, callback=None):
        self.onSwitchEvent([partial(self.__faderCallback, state, callback)])

    def __faderCallback(self, state, callback):
        if self._state != state:
            self._state = state
            super(FaderSwitcher, self).switchTo(state, callback)
        elif callback:
            callback()

    @sf_lobby
    def __app(self):
        return None

    def __initFader(self):
        app = self.__app
        if app and app.faderManager:
            app.faderManager.addFadeEvent(self.onSwitchEvent)
