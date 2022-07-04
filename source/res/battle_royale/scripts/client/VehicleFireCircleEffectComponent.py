# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleFireCircleEffectComponent.py
import BigWorld
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from VehicleAbilityBaseComponent import VehicleAbilityBaseComponent

class VehicleFireCircleEffectComponent(VehicleAbilityBaseComponent):
    __CLASS_NAME = 'VehicleFireCircleEffectComponent'
    __TIMER_VIEW_ID = VEHICLE_VIEW_STATE.FIRE_CIRCLE
    __MARKER_ID = BATTLE_MARKER_STATES.FIRE_CIRCLE_STATE

    def __init__(self):
        super(VehicleFireCircleEffectComponent, self).__init__(self.__TIMER_VIEW_ID, self.__MARKER_ID)

    def _getDuration(self):

        def isCandidate(key, comp):
            return key.startswith(self.__CLASS_NAME) if key else isinstance(comp, VehicleFireCircleEffectComponent)

        compItems = self.entity.dynamicComponents.items()
        allTimes = [ comp.finishTime for key, comp in compItems if isCandidate(key, comp) ]
        return max(max(allTimes) - BigWorld.serverTime(), 0.0) if allTimes else 0.0
