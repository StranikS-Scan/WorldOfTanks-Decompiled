# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleFireCircleEffectComponent.py
from typing import TYPE_CHECKING
from battle_royale.gui.constants import BattleRoyaleEquipments
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from VehicleAbilityBaseComponent import VehicleAbilityBaseComponent
from items import vehicles
from shared_utils import first
if TYPE_CHECKING:
    from battle_royale_artefacts import FireCircle

class VehicleFireCircleEffectComponent(VehicleAbilityBaseComponent):
    __CLASS_NAME = 'VehicleFireCircleEffectComponent'
    __TIMER_VIEW_ID = VEHICLE_VIEW_STATE.FIRE_CIRCLE
    __MARKER_ID = BATTLE_MARKER_STATES.FIRE_CIRCLE_STATE

    def __init__(self):
        super(VehicleFireCircleEffectComponent, self).__init__(self.__TIMER_VIEW_ID, self.__MARKER_ID)

    def _getDuration(self):
        return int(self.getEquipment().influenceZone.timer)

    @staticmethod
    def getEquipment():
        equipmentID = vehicles.g_cache.equipmentIDs().get(BattleRoyaleEquipments.FIRE_CIRCLE)
        equipment = vehicles.g_cache.equipments()[equipmentID]
        return equipment

    def _destroy(self):
        super(VehicleFireCircleEffectComponent, self)._destroy()
        otherComp = first([ comp for comp in self.entity.dynamicComponents.values() if isinstance(comp, VehicleFireCircleEffectComponent) and comp is not self ])
        if otherComp:
            otherComp.set_finishTime()
