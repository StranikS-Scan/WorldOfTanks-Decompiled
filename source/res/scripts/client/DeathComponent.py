# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DeathComponent.py
from __future__ import absolute_import
import BigWorld
import CGF
import GenericComponents
import Math
from cgf_components_common.state_components import DeathComponentDescriptor, SpawnOnDeathComponent, RemoveOnDeathComponent
from cgf_client_common.entity_dyn_components import ReplicableDynamicScriptComponent
from cgf_script.registration import registerReplicableComponent
from cgf_components.on_death_components import SoundOnDeathComponent, EffectOnDeathComponent, ChangeModelOnDeathComponent
from debug_utils import LOG_DEBUG_DEV
from functools import partial

@registerReplicableComponent
class DeathComponent(ReplicableDynamicScriptComponent, DeathComponentDescriptor):
    pass


def removeGameObject(go):
    go.destroy()


def loadPrefab(prefabPath, go, tr, loadIntoHierarchy):
    if loadIntoHierarchy:
        CGF.loadAndCreatePrefabWithParent(prefabPath, go, Math.Vector3(0, 0, 0))
    else:
        CGF.loadAndCreatePrefab(prefabPath, go.spaceID, tr)


def changeModel(go, modelPath, spaceID):
    queue = CGF.CommandQueue(spaceID)
    queue.removeComponent(go, GenericComponents.DynamicModelComponent)
    queue.createComponent(go, GenericComponents.DynamicModelComponent, modelPath)


class DeathComponentSystem(CGF.System):
    RemoveOnDeathActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactHas(DeathComponent), CGF.Ro(RemoveOnDeathComponent))
    SpawnOnDeathActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactHas(DeathComponent), CGF.Ro(SpawnOnDeathComponent), CGF.Ro(CGF.TransformComponent))
    SoundOnDeathComponentActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactHas(DeathComponent), CGF.Ro(SoundOnDeathComponent), CGF.Ro(CGF.TransformComponent))
    EffectOnDeathComponentActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactHas(DeathComponent), CGF.Ro(EffectOnDeathComponent), CGF.Ro(CGF.TransformComponent))
    ChangeModelOnDeathComponentActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactHas(DeathComponent), CGF.Rw(ChangeModelOnDeathComponent), CGF.OptRw(GenericComponents.DynamicModelComponent))
    ChangeModelOnDeathComponentDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.ReactHas(DeathComponent), CGF.Ro(ChangeModelOnDeathComponent), CGF.OptRw(GenericComponents.DynamicModelComponent))
    Reactions = CGF.Reactions(RemoveOnDeathActivated, SpawnOnDeathActivated, SoundOnDeathComponentActivated, EffectOnDeathComponentActivated, ChangeModelOnDeathComponentActivated, ChangeModelOnDeathComponentDeactivated)

    def update(self):
        spaceID = self.spaceID
        for go, change, model in self.reaction(self.ChangeModelOnDeathComponentDeactivated):
            if model:
                changeModel(go, change.initialModel, spaceID)

        for go, change, model in self.reaction(self.ChangeModelOnDeathComponentActivated):
            if model:
                LOG_DEBUG_DEV('Game object name=%s, id=%s changed his DynamicModelComponent because of death to a new one "%s"', go.name, go.id, change.modelPath)
                change.initialModel = model.getModelName()
                if change.delay == 0:
                    changeModel(go, change.modelPath, spaceID)
                else:
                    BigWorld.callback(change.delay, lambda obj=go, sid=spaceID, path=change.modelPath: changeModel(obj, path, sid))

        for go, remove in self.reaction(self.RemoveOnDeathActivated):
            LOG_DEBUG_DEV('Game object name=%s, id=%s was removed because of death', go.name, go.id)
            if remove.delay == 0:
                removeGameObject(go)
            BigWorld.callback(remove.delay, partial(removeGameObject, go))

        for go, spawn, tr in self.reaction(self.SpawnOnDeathActivated):
            LOG_DEBUG_DEV('Prefab "%s" was loaded because of death into Game object name=%s, id=%s', spawn.prefabPath, go.name, go.id)
            if spawn.delay == 0:
                loadPrefab(spawn.prefabPath, go, tr.worldPosition, spawn.attachToGO)
            BigWorld.callback(spawn.delay, partial(loadPrefab, spawn.prefabPath, go, tr.worldPosition, spawn.attachToGO))

        for go, sound, tr in self.reaction(self.SoundOnDeathComponentActivated):
            LOG_DEBUG_DEV('Sound prefab "%s" was loaded because of death into Game object name=%s, id=%s', sound.soundPath, go.name, go.id)
            if sound.delay == 0:
                loadPrefab(sound.soundPath, go, tr.worldPosition, sound.attachToGO)
            BigWorld.callback(sound.delay, partial(loadPrefab, sound.soundPath, go, tr.worldPosition, sound.attachToGO))

        for go, effect, tr in self.reaction(self.EffectOnDeathComponentActivated):
            LOG_DEBUG_DEV('Effect prefab "%s" was loaded because of death into Game object name=%s, id=%s', effect.effectPath, go.name, go.id)
            if effect.delay == 0:
                loadPrefab(effect.effectPath, go, tr.worldPosition, effect.attachToGO)
            BigWorld.callback(effect.delay, partial(loadPrefab, effect.effectPath, go, tr.worldPosition))
