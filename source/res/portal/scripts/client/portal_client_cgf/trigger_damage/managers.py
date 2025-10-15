# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/trigger_damage/managers.py
from functools import partial
import BigWorld
import CGF
import Math
import Sound
import Triggers
from GenericComponents import AnimatorComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from shared_utils import nextTick
from portal.sounds.sound_constants import GameplayVoiceovers, PortalBattleSound
from portal.sounds.sound_helpers import playVoiceover, play2DSound
from portal_common_cgf.portal_helpers import registerPortalManager, getVehicleFromGO
from portal_common_cgf.trigger_damage.components import AreaTriggerDamageComponent
from PortalBattleStateComponent import PortalBattleStateComponent

@registerPortalManager(CGF.DomainOption.DomainClient)
class AreaTriggerDamageManager(CGF.ComponentManager):
    __SENTINEL_STATE_MODELS_GO_NAME = 'sentinelStateModels'
    __SENTINEL_STATE_MODELS_PREFAB = 'content/CGFPrefabs/portal/sentinelStateModels.prefab'
    __SENTINEL_STATE_MODEL_NAME_TEMPLATE = 'model_state_{}'
    __SENTINEL_DAMAGE_PREFAB = 'content/CGFPrefabs/portal/sentinelDamage.prefab'

    def __init__(self):
        super(AreaTriggerDamageManager, self).__init__()
        PortalBattleStateComponent.onBossFightFinished += self.__onBossFightFinished
        PortalBattleStateComponent.onCampCaptured += self.__onCampCaptured

    def destroy(self):
        PortalBattleStateComponent.onCampCaptured -= self.__onCampCaptured
        PortalBattleStateComponent.onBossFightFinished -= self.__onBossFightFinished

    @onAddedQuery(CGF.GameObject, AreaTriggerDamageComponent)
    def onAdded(self, go, areaTriggerDamage):
        trigger = go.findComponentByType(Triggers.AreaTriggerComponent)
        if trigger is None:
            return
        else:
            areaTriggerDamage.reactionID = trigger.addEnterReaction(self.__onVehicleDamage)
            areaTriggerDamage.damageState = len(areaTriggerDamage.damageStates) - 1
            CGF.loadGameObjectIntoHierarchy(self.__SENTINEL_STATE_MODELS_PREFAB, go, Math.Vector3(0, 0, 0), self.__onModelPrefabLoaded)
            sound3D = go.findComponentByType(Sound.Sound3DComponent)
            if not sound3D:
                go.createComponent(Sound.Sound3DComponent, 'sentinel_on', PortalBattleSound.SENTINEL_ON, True)
            return

    @onRemovedQuery(CGF.GameObject, AreaTriggerDamageComponent)
    def onRemoved(self, go, areaTriggerDamage):
        trigger = go.findComponentByType(Triggers.AreaTriggerComponent)
        if trigger is None:
            return
        else:
            trigger.removeEnterReaction(areaTriggerDamage.reactionID)
            return

    @property
    def battleState(self):
        return BigWorld.player().arena.arenaInfo.portalBattleStateComponent

    def __onVehicleDamage(self, whoGO, areaTriggerGO):
        if not self.__isGOShouldReact(whoGO):
            return
        damageState = self.battleState.getCampsCount() - self.battleState.getCapturedCampsCount()
        if damageState <= 0:
            return
        CGF.loadGameObjectIntoHierarchy(self.__SENTINEL_DAMAGE_PREFAB, whoGO, Math.Vector3(0, 0, 0))
        vehicle = getVehicleFromGO(whoGO, self.spaceID)
        if vehicle and vehicle.id == BigWorld.player().playerVehicleID:
            playVoiceover(GameplayVoiceovers.SENTINEL_DAMAGED_VEHICLE)
            play2DSound(PortalBattleSound.SENTINEL_DAMAGE)

    def __onBossFightFinished(self):
        self.__disableSentinels()

    def __onCampCaptured(self, campGO):
        query = CGF.Query(self.spaceID, (CGF.GameObject, AreaTriggerDamageComponent))
        for go, triggerDamage in query:
            self.__weakenSentinel(go, triggerDamage)
            if triggerDamage.damageState <= 0:
                self.__onSentinelExhausted(go, triggerDamage)

    def __weakenSentinel(self, go, triggerDamage):
        hm = CGF.HierarchyManager(self.spaceID)
        for child in hm.getChildren(go):
            if child.name == self.__SENTINEL_STATE_MODELS_GO_NAME:
                self.__updateSentinelModel(hm, child, triggerDamage)
                break

        triggerDamage.damageState -= 1

    def __onSentinelExhausted(self, go, triggerDamage):
        sentinelOnSound3D = go.findComponentByType(Sound.Sound3DComponent)
        if sentinelOnSound3D:
            go.removeComponent(sentinelOnSound3D)
        go.createComponent(Sound.Sound3DComponent, 'sentinel_off', PortalBattleSound.SENTINEL_OFF, True)

    def __updateSentinelModel(self, hm, sentinelModelsGO, triggerDamage):
        stateModelName = self.__SENTINEL_STATE_MODEL_NAME_TEMPLATE.format(triggerDamage.damageState)
        for stateModel in hm.getChildren(sentinelModelsGO):
            if stateModel.name == stateModelName:
                animator = stateModel.findComponentByType(AnimatorComponent)
                if animator:
                    animator.start()
                    break

    def __disableSentinels(self):
        query = CGF.Query(self.spaceID, (CGF.GameObject, AreaTriggerDamageComponent))
        for go, _ in query:
            go.deactivate()

    def __onModelPrefabLoaded(self, modelsGO):
        updateSentinelState = partial(self.__updateSentinelState, modelsGO)
        nextTick(updateSentinelState)()

    def __updateSentinelState(self, modelsGO):
        hm = CGF.HierarchyManager(self.spaceID)
        triggerDamageGO = hm.getParent(modelsGO)
        triggerDamage = triggerDamageGO.findComponentByType(AreaTriggerDamageComponent)
        capturedCampsCount = self.battleState.getCapturedCampsCount()
        for _ in range(capturedCampsCount):
            self.__weakenSentinel(triggerDamageGO, triggerDamage)

    def __isGOShouldReact(self, go):
        vehicle = getVehicleFromGO(go, self.spaceID)
        if not vehicle:
            return False
        arenaDP = vehicle.guiSessionProvider.getArenaDP()
        vInfos = arenaDP.getVehicleInfo(vehicle.id)
        return arenaDP.isAllyTeam(vInfos.team)
