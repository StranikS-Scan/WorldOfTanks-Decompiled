# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/GunReloadBoost.py
from cache import cached_property
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from view_state_component import ViewStateComponent

class GunReloadBoost(ViewStateComponent):

    @cached_property
    def _sessionProvider(self):
        return dependency.instance(IBattleSessionProvider)

    def onReloadBoost(self):
        from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
        if self.entity.id == self._sessionProvider.shared.vehicleState.getControllingVehicleID():
            self._sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.GUN_RELOAD_BOOST, None)
        return
