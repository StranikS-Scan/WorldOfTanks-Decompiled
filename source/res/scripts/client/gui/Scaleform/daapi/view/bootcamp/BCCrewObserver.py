# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCCrewObserver.py
import Event
from gui.Scaleform.daapi.view.meta.BCCrewObserverMeta import BCCrewObserverMeta

class BCCrewObserver(BCCrewObserverMeta):

    def __init__(self):
        super(BCCrewObserver, self).__init__()
        self.onTankmanClickEvent = Event.Event()
        self.onDropDownClosedEvent = Event.Event()

    def onTankmanClick(self, slotIndex):
        self.onTankmanClickEvent(slotIndex)

    def onDropDownClosed(self, slotIndex):
        self.onDropDownClosedEvent(slotIndex)

    def _dispose(self):
        self.onTankmanClickEvent.clear()
        self.onDropDownClosedEvent.clear()
        super(BCCrewObserver, self)._dispose()
