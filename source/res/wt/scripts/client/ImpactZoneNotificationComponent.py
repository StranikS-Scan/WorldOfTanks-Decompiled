# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: wt/scripts/client/ImpactZoneNotificationComponent.py
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.battle_constants import HyperionTimerViewState

class ImpactZoneNotificationComponent(DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def set_impactAreaInfo(self, _=None):
        if self.impactAreaInfo is None:
            return
        else:
            self.__updateImpactNotification(self.impactAreaInfo['timeBeforeDamage'], self.impactAreaInfo['isVisible'])
            return

    def __updateImpactNotification(self, timeBeforeDamage, isVisible):
        value = HyperionTimerViewState(isVisible, timeBeforeDamage, BigWorld.serverTime() + timeBeforeDamage)
        vehicle = self.entity
        if vehicle is not None:
            self.__guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.WT_HYPERION_WARNING_CHARGING, value, vehicleID=vehicle.id)
        return
