# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWBuffShowCannotBeDamagedMarker.py
from __future__ import absolute_import
import BigWorld
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from HWArenaPhasesComponent import HWArenaPhasesComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _FET
from halloween_common.halloween_constants import BOSS_ROLE_TAG

def isInvulnerableBoss(vehicleID):
    vehicle = BigWorld.entities.get(vehicleID)
    if vehicle is None:
        return False
    elif BOSS_ROLE_TAG not in vehicle.typeDescriptor.type.tags:
        return False
    else:
        arenaPhases = HWArenaPhasesComponent.getInstance()
        return not arenaPhases.isBossVulnerable if arenaPhases is not None else False


class HWBuffShowCannotBeDamagedMarker(DynamicScriptComponent):
    _guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, *args, **kwargs):
        super(HWBuffShowCannotBeDamagedMarker, self).__init__(*args, **kwargs)
        self._alreadyShown = False

    def onDestroy(self):
        if self._isAvatarReady and not self._alreadyShown:
            self._setVehicleState()
        super(HWBuffShowCannotBeDamagedMarker, self).onDestroy()

    def _onAvatarReady(self):
        super(HWBuffShowCannotBeDamagedMarker, self)._onAvatarReady()
        self._setVehicleState()

    def _setVehicleState(self):
        self._alreadyShown = True
        if self.entity.isDestroyed:
            return
        isInvulnerable = isInvulnerableBoss(self.entity.id)
        feedback = self._guiSessionProvider.shared.feedback
        if isInvulnerable and feedback:
            feedback.setVehicleState(self.entity.id, _FET.VEHICLE_HIT)
