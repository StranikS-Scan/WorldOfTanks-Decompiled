# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/sequence_components.py
import CGF
import GenericComponents
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister

@registerComponent
class OnDisappearPrefabSpawnComponent(object):
    editorTitle = 'On Disappear Prefab Spawner'
    category = 'Sequence'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    prefab = ComponentProperty(type=CGFMetaTypes.STRING, editorName='prefab', value='', annotations={'path': '*.prefab'})


@registerComponent
class OnAppearPrefabSpawnComponent(object):
    editorTitle = 'On Appear Prefab Spawner'
    category = 'Sequence'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    prefab = ComponentProperty(type=CGFMetaTypes.STRING, editorName='prefab', value='', annotations={'path': '*.prefab'})


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class PrefabSpawnerManager(CGF.ComponentManager):

    @onAddedQuery(OnAppearPrefabSpawnComponent, GenericComponents.TransformComponent, tickGroup='PostHierarchy')
    def onAppear(self, spawner, transform):
        CGF.loadGameObject(spawner.prefab, self.spaceID, transform.worldTransform, self._onGameObjectLoaded)

    @onRemovedQuery(OnDisappearPrefabSpawnComponent, GenericComponents.TransformComponent)
    def onDisappear(self, spawner, transform):
        CGF.loadGameObject(spawner.prefab, self.spaceID, transform.worldTransform, self._onGameObjectLoaded)

    @staticmethod
    def _onGameObjectLoaded(gameObject):
        gameObject.activate()
        gameObject.transferOwnershipToWorld()
