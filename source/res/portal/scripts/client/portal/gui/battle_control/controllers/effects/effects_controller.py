# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/battle_control/controllers/effects/effects_controller.py
import typing
from functools import partial
import BigWorld
import CGF
import Math
import BattleReplay
from GenericComponents import RemoveGoDelayedComponent
from gui.battle_control.controllers.interfaces import IBattleController
from PortalBattleStateComponent import PortalBattleStateComponent
from portal_common_cgf.portal_helpers import WAVE_LABEL_PREFIX, CAMP_LABEL_PREFIX, ASSISTANT_LABEL
from portal_constants import PORTAL_BATTLE_CTRL_ID
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, List
    from gui.battle_control import BattleSessionSetup

class EffectsController(IBattleController):
    __slots__ = ()
    __BOT_SPAWN_PREFAB = 'content/CGFPrefabs/portal/botSpawn.prefab'
    __HEAL_PREFAB = 'content/CGFPrefabs/portal/playerHeal.prefab'
    __BOT_SPAWN_PREFAB_REMOVE_DELAY = 3.0
    __HEAL_PREFAB_REMOVE_DELAY = 5.0

    def __init__(self, setup):
        super(EffectsController, self).__init__()

    def startControl(self, *args):
        PortalBattleStateComponent.onBotVehiclePreparing += self.__onBotVehiclePreparing
        PortalBattleStateComponent.onCampCaptureHealApplied += self.__onCampCaptureHealApplied

    def stopControl(self):
        PortalBattleStateComponent.onBotVehiclePreparing -= self.__onBotVehiclePreparing
        PortalBattleStateComponent.onCampCaptureHealApplied -= self.__onCampCaptureHealApplied

    def getControllerID(self):
        return PORTAL_BATTLE_CTRL_ID.EFFECTS_CTRL

    def __onCampCaptureHealApplied(self, vehicleIDs):
        for vehicleID in vehicleIDs:
            vehicle = BigWorld.entities.get(vehicleID, None)
            if vehicle is not None and vehicle.entityGameObject is not None:
                CGF.loadGameObjectIntoHierarchy(self.__HEAL_PREFAB, vehicle.entityGameObject, Math.Vector3(0, 0, 0), partial(self.__onEffectLoaded, removeDelay=self.__HEAL_PREFAB_REMOVE_DELAY))

        return

    def __onBotVehiclePreparing(self, spawnData):
        botLabel = spawnData.get('extra', {}).get('label')
        if not botLabel:
            return None
        else:
            position, yaw = spawnData.get('position', (None, None))
            if not position:
                return None
            position = Math.Vector3(*position)
            for labelPrefix in (WAVE_LABEL_PREFIX, CAMP_LABEL_PREFIX, ASSISTANT_LABEL):
                if botLabel.startswith(labelPrefix):
                    self.__loadEffect(self.__BOT_SPAWN_PREFAB, position, yaw, self.__BOT_SPAWN_PREFAB_REMOVE_DELAY)
                    break

            return None

    def __loadEffect(self, prefabPath, position, yaw, removeDelay=None):
        spaceID = BigWorld.player().spaceID
        transform = Math.createRTMatrix(Math.Vector3(yaw, 0.0, 0.0), position)
        CGF.loadGameObject(prefabPath, spaceID, transform, partial(self.__onEffectLoaded, removeDelay=removeDelay))

    def __onEffectLoaded(self, go, removeDelay):
        if removeDelay:
            go.createComponent(RemoveGoDelayedComponent, removeDelay)


class ReplayEffectsController(EffectsController):
    pass


def createPortalEffectsController(setup):
    return ReplayEffectsController(setup) if BattleReplay.g_replayCtrl.isPlaying else EffectsController(setup)
