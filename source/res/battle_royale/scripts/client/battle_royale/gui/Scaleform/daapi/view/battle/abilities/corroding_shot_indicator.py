# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/abilities/corroding_shot_indicator.py
import BigWorld
from helpers import dependency
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import EQUIPMENT_STAGES
from gui.Scaleform.daapi.view.meta.CorrodingShotIndicatorMeta import CorrodingShotIndicatorMeta
from battle_royale.gui.constants import BattleRoyaleEquipments
from Event import EventsSubscriber

class CorrodingShotIndicator(CorrodingShotIndicatorMeta, IAbstractPeriodView):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(CorrodingShotIndicator, self).__init__()
        self.__isEnabled = False
        self._es = EventsSubscriber()
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onEquipmentComponentUpdated.subscribe(self.__onEquipmentComponentUpdated, BattleRoyaleEquipments.CORRODING_SHOT)
        ctrl = self.__sessionProvider.shared.crosshair
        if ctrl is not None:
            self._es.subscribeToEvent(ctrl.onCrosshairPositionChanged, self.__onCrosshairPositionChanged)
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            self._es.subscribeToEvent(ctrl.onVehicleControlling, self.__onVehicleChanged)
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            self._es.subscribeToEvent(player.inputHandler.onCameraChanged, self.__onCameraChanged)
        return

    def _destroy(self):
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onEquipmentComponentUpdated.unsubscribe(self.__onEquipmentComponentUpdated)
        self._es.unsubscribeFromAllEvents()
        self.__disable()
        super(CorrodingShotIndicator, self)._destroy()
        return

    def __onEquipmentComponentUpdated(self, equipmentName, vehicleID, abilityInfo):
        if abilityInfo.stage == EQUIPMENT_STAGES.PREPARING:
            self.__enable()
        else:
            self.__disable()

    def __onVehicleChanged(self, vehicle):
        equipments = self.__sessionProvider.shared.equipments.getEquipments()
        eq = [ eq for eq in equipments.itervalues() if eq.getDescriptor().name == BattleRoyaleEquipments.CORRODING_SHOT ]
        if not eq and self.__isEnabled:
            self.__disable()

    def __onCrosshairPositionChanged(self, *args):
        crosshairCtrl = self.__sessionProvider.shared.crosshair
        scaledPosition = crosshairCtrl.getScaledPosition()
        self.as_updateLayoutS(*scaledPosition)

    def __enable(self):
        self.__isEnabled = True
        self.as_showS()

    def __disable(self):
        self.__isEnabled = False
        self.as_hideS()

    def __onCameraChanged(self, cameraName, currentVehicleId=None):
        if cameraName == 'video':
            self.__disable()
