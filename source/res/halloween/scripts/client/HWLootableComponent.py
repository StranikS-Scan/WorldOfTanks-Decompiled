# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWLootableComponent.py
from __future__ import absolute_import
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from halloween.gui.shared.events import HWBattleLootEvent
from script_component.DynamicScriptComponent import DynamicScriptComponent
from Event import Event, EventManager

class HWLootableComponent(DynamicScriptComponent):

    def __init__(self, *args, **kwargs):
        super(HWLootableComponent, self).__init__(*args, **kwargs)
        self._eManager = EventManager()
        self.onStartCapturing = Event(self._eManager)
        self.onStopCapturing = Event(self._eManager)
        self.onCapturingEntitiesChanged = Event(self._eManager)
        self._capturingUpdate()
        self._onInitialised()

    def set_isCapturing(self, *args, **kwargs):
        self._capturingUpdate()

    def set_looterEntities(self, *args, **kwargs):
        self.onCapturingEntitiesChanged()

    def onDestroy(self):
        self._eManager.clear()
        super(HWLootableComponent, self).onDestroy()

    def onVehicleStartCapturing(self, vehID):
        g_eventBus.handleEvent(HWBattleLootEvent(HWBattleLootEvent.VEH_CAPTURING_START, {'loot': self,
         'vehID': vehID}), EVENT_BUS_SCOPE.BATTLE)

    def onVehicleCancelCapturing(self, vehID):
        g_eventBus.handleEvent(HWBattleLootEvent(HWBattleLootEvent.VEH_CAPTURING_CANCEL, {'loot': self,
         'vehID': vehID}), EVENT_BUS_SCOPE.BATTLE)

    def onLootCapturingSucceeded(self, vehID, vehIDs):
        g_eventBus.handleEvent(HWBattleLootEvent(HWBattleLootEvent.CAPTURED, {'loot': self,
         'vehID': vehID,
         'vehIDs': vehIDs}), EVENT_BUS_SCOPE.BATTLE)

    def _onInitialised(self):
        g_eventBus.handleEvent(HWBattleLootEvent(HWBattleLootEvent.APPEAR, {'loot': self}), EVENT_BUS_SCOPE.BATTLE)

    def _capturingUpdate(self):
        if self.startTime == 0:
            self.onStopCapturing()
            return
        self.onStartCapturing(self.startTime, self.captureTime)
