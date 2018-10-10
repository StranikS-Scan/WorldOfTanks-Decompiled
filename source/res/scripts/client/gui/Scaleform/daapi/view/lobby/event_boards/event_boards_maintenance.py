# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_boards_maintenance.py
from gui.Scaleform.daapi.view.meta.MaintenanceComponentMeta import MaintenanceComponentMeta
import Event

class EventBoardsMaintenance(MaintenanceComponentMeta):

    def __init__(self):
        super(EventBoardsMaintenance, self).__init__()
        self.onRefresh = Event.Event()

    def refresh(self):
        self.onRefresh()
