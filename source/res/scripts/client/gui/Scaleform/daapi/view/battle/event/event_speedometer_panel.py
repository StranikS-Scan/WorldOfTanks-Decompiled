# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/event_speedometer_panel.py
from gui.Scaleform.daapi.view.meta.FestivalRaceSpeedometerMeta import FestivalRaceSpeedometerMeta
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class EventSpeedometerPanel(FestivalRaceSpeedometerMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(EventSpeedometerPanel, self)._populate()
        self.__addListeners()

    def __addListeners(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated += self.__onEquipmentUpdated
        return

    def __removeListeners(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        eqCtrl = self.sessionProvider.shared.equipments
        if eqCtrl is not None:
            eqCtrl.onEquipmentUpdated -= self.__onEquipmentUpdated
        return

    def __onEquipmentUpdated(self, intCD, item):
        self.as_updateEquipmentStageS(item.getStage())

    def __onVehicleStateUpdated(self, stateID, value):
        if stateID == VEHICLE_VIEW_STATE.SWITCHING:
            self.as_updateSpeedS(0)
        if stateID == VEHICLE_VIEW_STATE.SPEED:
            self.as_updateSpeedS(value)

    def _dispose(self):
        self.as_resetS()
        self.__removeListeners()
        super(EventSpeedometerPanel, self)._dispose()
