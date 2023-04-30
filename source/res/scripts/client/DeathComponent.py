# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DeathComponent.py
import BigWorld
import CGF
import GenericComponents
import Math
from cgf_components_common.state_components import DeathComponent as DeathComponentCGF, SpawnOnDeathComponent, RemoveOnDeathComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from cgf_components.on_death_components import SoundOnDeathComponent, EffectOnDeathComponent, ChangeModelOnDeathComponent
from debug_utils import LOG_DEBUG_DEV

class DeathComponent(BigWorld.DynamicScriptComponent, DeathComponentCGF):
    pass


def removeGameObject(gameObject):
    CGF.removeGameObject(gameObject)


def loadPrefab(prefabPath, gameObject, transform, loadIntoHierarchy):
    if loadIntoHierarchy:
        CGF.loadGameObjectIntoHierarchy(prefabPath, gameObject, Math.Vector3(0, 0, 0))
    else:
        CGF.loadGameObject(prefabPath, gameObject.spaceID, transform)


def changeModel(gameObject, dynamicModelComponent, modelPath):
    gameObject.removeComponent(dynamicModelComponent)
    gameObject.createComponent(GenericComponents.DynamicModelComponent, modelPath)


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor)
class DeathComponentManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, DeathComponent, RemoveOnDeathComponent, tickGroup='Simulation')
    def onAddedRemoveOnDeath(self, gameObject, _, removeOnDeathComponent):
        LOG_DEBUG_DEV('Game object name=%s, id=%s was removed because of death', gameObject.name, gameObject.id)
        if removeOnDeathComponent.delay == 0:
            removeGameObject(gameObject)
        else:
            BigWorld.callback(removeOnDeathComponent.delay, lambda : removeGameObject(gameObject))

    @onAddedQuery(CGF.GameObject, DeathComponent, SpawnOnDeathComponent, GenericComponents.TransformComponent)
    def onAddedSpawnOnDeath(self, gameObject, _, spawnOnDeathComponent, transform):
        LOG_DEBUG_DEV('Prefab "%s" was loaded because of death into Game object name=%s, id=%s', spawnOnDeathComponent.prefabPath, gameObject.name, gameObject.id)
        if spawnOnDeathComponent.delay == 0:
            loadPrefab(spawnOnDeathComponent.prefabPath, gameObject, transform.worldPosition, spawnOnDeathComponent.attachToGO)
        else:
            BigWorld.callback(spawnOnDeathComponent.delay, lambda : loadPrefab(spawnOnDeathComponent.prefabPath, gameObject, transform.worldPosition, spawnOnDeathComponent.attachToGO))

    @onAddedQuery(CGF.GameObject, DeathComponent, SoundOnDeathComponent, GenericComponents.TransformComponent)
    def onAddedSoundOnDeath(self, gameObject, _, soundOnDeathComponent, transform):
        LOG_DEBUG_DEV('Sound prefab "%s" was loaded because of death into Game object name=%s, id=%s', soundOnDeathComponent.soundPath, gameObject.name, gameObject.id)
        if soundOnDeathComponent.delay == 0:
            loadPrefab(soundOnDeathComponent.soundPath, gameObject, transform.worldPosition, soundOnDeathComponent.attachToGO)
        else:
            BigWorld.callback(soundOnDeathComponent.delay, lambda : loadPrefab(soundOnDeathComponent.soundPath, gameObject, transform.worldPosition, soundOnDeathComponent.attachToGO))

    @onAddedQuery(CGF.GameObject, DeathComponent, EffectOnDeathComponent, GenericComponents.TransformComponent)
    def onAddedEffectOnDeath(self, gameObject, _, effectOnDeathComponent, transform):
        LOG_DEBUG_DEV('Effect prefab "%s" was loaded because of death into Game object name=%s, id=%s', effectOnDeathComponent.effectPath, gameObject.name, gameObject.id)
        if effectOnDeathComponent.delay == 0:
            loadPrefab(effectOnDeathComponent.effectPath, gameObject, transform.worldPosition, effectOnDeathComponent.attachToGO)
        else:
            BigWorld.callback(effectOnDeathComponent.delay, lambda : loadPrefab(effectOnDeathComponent.effectPath, gameObject, transform.worldPosition, effectOnDeathComponent.attachToGO))

    @onAddedQuery(CGF.GameObject, DeathComponent, ChangeModelOnDeathComponent)
    def onAddedChangeModelOnDeath(self, gameObject, _, changeModelOnDeathComponent):
        dynamicModelComponent = gameObject.findComponentByType(GenericComponents.DynamicModelComponent)
        if dynamicModelComponent:
            LOG_DEBUG_DEV('Game object name=%s, id=%s changed his DynamicModelComponent because of death to a new one "%s"', gameObject.name, gameObject.id, changeModelOnDeathComponent.modelPath)
            changeModelOnDeathComponent.initialModel = dynamicModelComponent.getModelName()
            if changeModelOnDeathComponent.delay == 0:
                changeModel(gameObject, dynamicModelComponent, changeModelOnDeathComponent.modelPath)
            else:
                BigWorld.callback(changeModelOnDeathComponent.delay, lambda : changeModel(gameObject, dynamicModelComponent, changeModelOnDeathComponent.modelPath))

    @onRemovedQuery(CGF.GameObject, DeathComponent, ChangeModelOnDeathComponent)
    def onRemovedChangeModelOnDeath(self, gameObject, _, changeModelOnDeathComponent):
        dynamicModelComponent = gameObject.findComponentByType(GenericComponents.DynamicModelComponent)
        if dynamicModelComponent:
            changeModel(gameObject, dynamicModelComponent, changeModelOnDeathComponent.initialModel)
