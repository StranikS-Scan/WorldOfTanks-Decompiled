# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTImpactZoneNotificationComponent.py
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers import dependency
from constants import IS_VS_EDITOR
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger.gui.battle_control.white_tiger_battle_constants import VEHICLE_VIEW_STATE
from white_tiger_common.wt_constants import WTHyperionTimerViewState
if not IS_VS_EDITOR:
    from helpers.CallbackDelayer import CallbackDelayer

class WTImpactZoneNotificationComponent(DynamicScriptComponent):
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(WTImpactZoneNotificationComponent, self).__init__()
        self.__cd = CallbackDelayer()

    def set_impactAreaInfo(self, _=None):
        if self.impactAreaInfo is None:
            return
        else:
            self.__updateImpactNotification(self.impactAreaInfo['timeBeforeDamage'], self.impactAreaInfo['isVisible'])
            self.__cd.delayCallback(self.impactAreaInfo['timeBeforeDamage'], self.__onCountdownEnd)
            return

    def onDestroy(self):
        super(WTImpactZoneNotificationComponent, self).onDestroy()
        self.__updateImpactNotification(0.0, False)
        self.__cd.destroy()
        self.__cd = None
        return

    def __onCountdownEnd(self):
        self.__updateImpactNotification(0.0, True)
        return None

    def __updateImpactNotification(self, timeBeforeDamage, isVisible):
        value = WTHyperionTimerViewState(isVisible, timeBeforeDamage, BigWorld.serverTime() + timeBeforeDamage)
        vehicle = self.entity
        if vehicle is not None:
            self.__guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.WT_HYPERION_WARNING_CHARGING, value, vehicleID=vehicle.id)
        return
