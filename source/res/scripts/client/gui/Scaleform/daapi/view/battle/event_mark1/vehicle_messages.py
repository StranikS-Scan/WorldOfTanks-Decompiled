# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event_mark1/vehicle_messages.py
from gui.Scaleform.daapi.view.battle.shared import messages
from gui.battle_control import g_sessionProvider

class Mark1VehicleMessages(messages.VehicleMessages):

    def _addGameListeners(self):
        super(Mark1VehicleMessages, self)._addGameListeners()
        vehicleCtrl = g_sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onRespawnBaseMoving += self.__onRrespawnBaseMoving
        return

    def _removeGameListeners(self):
        vehicleCtrl = g_sessionProvider.shared.vehicleState
        if vehicleCtrl is not None:
            vehicleCtrl.onRespawnBaseMoving -= self.__onRrespawnBaseMoving
        super(Mark1VehicleMessages, self)._removeGameListeners()
        return

    def __onRrespawnBaseMoving(self):
        self.clear()
