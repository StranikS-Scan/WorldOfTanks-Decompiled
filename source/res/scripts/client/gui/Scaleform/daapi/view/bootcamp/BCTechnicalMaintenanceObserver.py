# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCTechnicalMaintenanceObserver.py
import Event
from gui.Scaleform.daapi.view.meta.BCTechnicalMaintenanceObserverMeta import BCTechnicalMaintenanceObserverMeta

class BCTechnicalMaintenanceObserver(BCTechnicalMaintenanceObserverMeta):

    def __init__(self):
        super(BCTechnicalMaintenanceObserver, self).__init__()
        self.onDropDownOpenEvent = Event.Event()
        self.onDropDownCloseEvent = Event.Event()
        self.onSlotSelectedEvent = Event.Event()

    def onDropDownOpen(self, index):
        self.onDropDownOpenEvent(index)

    def onDropDownClose(self, index):
        self.onDropDownCloseEvent(index)

    def onSlotSelected(self, slotId, index):
        self.onSlotSelectedEvent(slotId, index)

    def _dispose(self):
        self.onDropDownOpenEvent.clear()
        self.onDropDownCloseEvent.clear()
        self.onSlotSelectedEvent.clear()
        self.onDropDownOpenEvent = None
        self.onDropDownCloseEvent = None
        self.onSlotSelectedEvent = None
        super(BCTechnicalMaintenanceObserver, self)._dispose()
        return
