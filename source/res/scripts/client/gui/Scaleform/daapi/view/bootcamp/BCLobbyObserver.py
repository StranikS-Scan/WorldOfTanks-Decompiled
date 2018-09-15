# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCLobbyObserver.py
import Event
from gui.Scaleform.daapi.view.meta.BCLobbyObserverMeta import BCLobbyObserverMeta
from gui.Scaleform.genConsts.BOOTCAMP_ALIASES import BOOTCAMP_ALIASES

class BCLobbyObserver(BCLobbyObserverMeta):

    def __init__(self):
        super(BCLobbyObserver, self).__init__()
        self.onAnimationsCompleteEvent = Event.Event()

    def registerAppearManager(self, component):
        self.registerFlashComponent(component, BOOTCAMP_ALIASES.BOOTCAMP_APPEAR_MANAGER)

    def onAnimationsComplete(self):
        self.onAnimationsCompleteEvent()

    def _dispose(self):
        self.onAnimationsCompleteEvent.clear()
        super(BCLobbyObserver, self)._dispose()
