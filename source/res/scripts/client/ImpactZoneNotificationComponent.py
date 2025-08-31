# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ImpactZoneNotificationComponent.py
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control.battle_constants import HyperionTimerViewState
from white_tiger_common.wt_constants import WT_TAGS

class ImpactZoneNotificationComponent(DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def set_impactAreaInfo(self, _=None):
        if self.impactAreaInfo is None:
            return
        else:
            self.__updateImpactNotification()
            return

    def __updateImpactNotification(self):
        value = HyperionTimerViewState(self.impactAreaInfo['isVisible'], self.impactAreaInfo['timeBeforeDamage'], BigWorld.serverTime() + self.impactAreaInfo['timeBeforeDamage'])
        vehicle = self.entity
        viewState = VEHICLE_VIEW_STATE.WT_HYPERION_WARNING_CHARGING
        if self.impactAreaInfo['bossType'] == WT_TAGS.WT_BOSS_2025:
            viewState = VEHICLE_VIEW_STATE.WT_HYPERION_2025_WARNING_CHARGING
        if vehicle is not None:
            self.__guiSessionProvider.invalidateVehicleState(viewState, value, vehicleID=vehicle.id)
        return
