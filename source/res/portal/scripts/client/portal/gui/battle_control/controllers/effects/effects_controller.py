# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/battle_control/controllers/effects/effects_controller.py
import typing
from functools import partial
import BigWorld
import CGF
import Math
import BattleReplay
from GenericComponents import RemoveGoDelayedComponent
from debug_utils import LOG_ERROR
from gui.battle_control.controllers.interfaces import IBattleController
from PortalBattleStateComponent import PortalBattleStateComponent
from portal_client_cgf.portal_components import SuperBossFightEffectComponent
from portal_common.portal_constants import BattleState
from portal_common_cgf.portal_helpers import WAVE_LABEL_PREFIX, CAMP_LABEL_PREFIX, ASSISTANT_LABEL, SUPER_BOSS_LABEL
from portal_constants import PORTAL_BATTLE_CTRL_ID
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, List
    from gui.battle_control import BattleSessionSetup

class EffectsController(IBattleController):
    __slots__ = ()
    __BOT_SPAWN_PREFAB = 'content/CGFPrefabs/portal/botSpawn.prefab'
    __BOT_SPAWN_PREFAB_REMOVE_DELAY = 3.0
    __SUPER_BOSS_FIGHT_RISE_EFFECT = 'riseEffect'
    __SUPER_BOSS_FIGHT_FLASH_EFFECT = 'riseFlashEffect'

    def __init__(self, setup):
        super(EffectsController, self).__init__()

    def startControl(self, *args):
        PortalBattleStateComponent.onBattleStateChanged += self.__onBattleStateChanged
        PortalBattleStateComponent.onBotVehiclePreparing += self.__onBotVehiclePreparing

    def stopControl(self):
        PortalBattleStateComponent.onBotVehiclePreparing -= self.__onBotVehiclePreparing
        PortalBattleStateComponent.onBattleStateChanged -= self.__onBattleStateChanged

    def getControllerID(self):
        return PORTAL_BATTLE_CTRL_ID.EFFECTS_CTRL

    def __onBattleStateChanged(self, battleState):
        if battleState == BattleState.SUPER_BOSS_FIGHT:
            self.__activateSuperBossFightEffectByName(self.__SUPER_BOSS_FIGHT_RISE_EFFECT)

    def __onBotVehiclePreparing(self, spawnData):
        botLabel = spawnData.get('extra', {}).get('label')
        if not botLabel:
            return None
        else:
            position, yaw = spawnData.get('position', (None, None))
            if not position:
                return None
            position = Math.Vector3(*position)
            if botLabel == SUPER_BOSS_LABEL:
                self.__activateSuperBossFightEffectByName(self.__SUPER_BOSS_FIGHT_FLASH_EFFECT)
                return None
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

    def __activateSuperBossFightEffectByName(self, name):
        spaceID = BigWorld.player().spaceID
        hm = CGF.HierarchyManager(spaceID)
        query = CGF.Query(spaceID, (CGF.GameObject, SuperBossFightEffectComponent))
        if len(query.values()) != 1:
            LOG_ERROR('There is must be exactly one SuperBossFightEffect')
        for go, _ in query:
            for child in hm.getChildrenIncludingInactive(go):
                if child.name == name:
                    child.activate()
                    return


class ReplayEffectsController(EffectsController):
    pass


def createPortalEffectsController(setup):
    return ReplayEffectsController(setup) if BattleReplay.g_replayCtrl.isPlaying else EffectsController(setup)
