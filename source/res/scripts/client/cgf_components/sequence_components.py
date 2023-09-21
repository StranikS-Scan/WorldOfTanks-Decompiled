# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/sequence_components.py
import CGF
import GenericComponents
import Math
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, registerManager, Rule

@registerComponent
class StageModifier(object):
    paramName = ComponentProperty(CGFMetaTypes.STRING, editorName='paramName', value='')


@registerComponent
class IdleEffectSpawner(object):
    start = ComponentProperty(CGFMetaTypes.STRING, editorName='Start', value='', annotations={'path': '*.seq'})
    startDuration = ComponentProperty(CGFMetaTypes.FLOAT, editorName='Start Duration', value=0.0)
    idle = ComponentProperty(CGFMetaTypes.STRING, editorName='Idle', value='', annotations={'path': '*.seq'})
    end = ComponentProperty(CGFMetaTypes.STRING, editorName='End', value='', annotations={'path': '*.seq'})
    endDuration = ComponentProperty(CGFMetaTypes.FLOAT, editorName='End Duration', value=0.0)
    followParent = ComponentProperty(CGFMetaTypes.BOOL, editorName='End follows parent', value=False)


class StageModifierManager(CGF.ComponentManager):
    stageQuery = CGF.QueryConfig(GenericComponents.BattleStage)

    @onAddedQuery(GenericComponents.AnimatorComponent, StageModifier)
    def onAdded(self, animator, stage):
        if not self.stageQuery.empty():
            bs = self.stageQuery.values()[0]
            value = float(bs.current) / bs.maximum
            animator.setFloatParam(stage.paramName, value)


@registerComponent
class OnAppearPrefabSpawner(object):
    prefab = ComponentProperty(type=CGFMetaTypes.STRING, editorName='prefab', value='', annotations={'path': '*.prefab'})


@registerComponent
class OnDisappearPrefabSpawner(object):
    prefab = ComponentProperty(type=CGFMetaTypes.STRING, editorName='prefab', value='', annotations={'path': '*.prefab'})


class PrefabSpawnerManager(CGF.ComponentManager):

    @onAddedQuery(OnAppearPrefabSpawner, GenericComponents.TransformComponent)
    def onAppear(self, spawner, transform):
        CGF.loadGameObject(spawner.prefab, self.spaceID, transform.worldTransform, self._onGameObjectLoaded)

    @onRemovedQuery(OnDisappearPrefabSpawner, GenericComponents.TransformComponent)
    def onDisappear(self, spawner, transform):
        CGF.loadGameObject(spawner.prefab, self.spaceID, transform.worldTransform, self._onGameObjectLoaded)

    def _onGameObjectLoaded(self, gameObject):
        gameObject.activate()
        gameObject.transferOwnershipToWorld()


class IdleEffectComponentManager(CGF.ComponentManager):

    @onAddedQuery(IdleEffectSpawner, CGF.GameObject)
    def onAdded(self, spawner, go):
        if spawner.start and spawner.startDuration:
            startWrapper = self.__createGO(spawner.start, 0.0, spawner.startDuration, go)
            startWrapper.activate()
            startWrapper.transferOwnershipToWorld()
        if spawner.idle:
            idleWrapper = self.__createGO(spawner.idle, spawner.startDuration, None, go)
            idleWrapper.activate()
            idleWrapper.transferOwnershipToWorld()
        return

    @onRemovedQuery(IdleEffectSpawner, CGF.GameObject)
    def onRemoved(self, spawner, go):
        if spawner.end and spawner.endDuration:
            endWrapper = self.__createGO(spawner.end, 0.0, spawner.endDuration)
            if spawner.followParent:
                endWrapper.createComponent(GenericComponents.TransformComponent, Math.Vector3())
                hierarchy = CGF.HierarchyManager(self.spaceID)
                parent = hierarchy.getParent(go)
                if parent:
                    endWrapper.createComponent(GenericComponents.HierarchyComponent, parent)
            else:
                transform = go.findComponentByType(GenericComponents.TransformComponent)
                if transform:
                    endWrapper.createComponent(GenericComponents.TransformComponent, transform.worldTransform)
            endWrapper.activate()
            endWrapper.transferOwnershipToWorld()

    def __createGO(self, resource, activationDelay=0.0, deactivationDelay=None, parent=None):
        go = CGF.GameObject(self.spaceID)
        if parent is not None:
            go.createComponent(GenericComponents.TransformComponent, Math.Vector3())
            go.createComponent(GenericComponents.HierarchyComponent, parent)
        go.createComponent(GenericComponents.AnimatorComponent, resource, activationDelay, 1.0, -1 if deactivationDelay is None else 1, True, '')
        if deactivationDelay is not None:
            go.createComponent(GenericComponents.RemoveGoDelayedComponent, deactivationDelay)
        return go


class SequenceRule(Rule):

    @registerManager(IdleEffectComponentManager)
    def reg1(self):
        return None

    @registerManager(PrefabSpawnerManager)
    def reg2(self):
        return None
