# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/common/frontline_cgf/epic_battles_components.py
import CGF
from GenericComponents import TransformComponent
from Physics import CollidersComponent
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
from constants import IS_CLIENT
from debug_utils import LOG_DEBUG
if IS_CLIENT:
    from GenericComponents import AnimatorComponent, RemoveGoDelayedComponent

@registerComponent
class SupplyComponent(object):
    domain = CGF.DomainOption.DomainServer
    category = 'Frontline'

    def __init__(self, callback=None):
        self.callback = callback


@registerComponent
class SupplySpawnComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Supply Spawn Animation'
    category = 'Frontline'
    prefabPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Prefab path', value='')


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainServer)
class SupplyComponentManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, SupplyComponent)
    def onAddedSupplyComponent(self, go, _):
        self.__logDebug('Create SupplyComponent on game object name={}, id={}', go.name, go.id)
        CGF.removeGameObject(go)

    @onRemovedQuery(CGF.GameObject, CollidersComponent, SupplyComponent, tickGroup='postHierarchyUpdate')
    def onRemovedSupplyComponent(self, go, _, supplyComponent):
        self.__logDebug('Remove SupplyComponent from game object name={}, id={}', go.name, go.id)
        supplyComponent.callback()

    @staticmethod
    def __logDebug(message, *args):
        LOG_DEBUG('[SupplyComponentManager]', message.format(*args))


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor, category='Frontline')
class EpicBattlesComponentManager(CGF.ComponentManager):

    def __init__(self, *args):
        super(EpicBattlesComponentManager, self).__init__(*args)
        self.__gameObject = {}

    @onAddedQuery(CGF.GameObject, SupplySpawnComponent, TransformComponent)
    def onAddedSupplyComponent(self, go, supplySpawnComponent, transform):

        def setGO(newGameObject):
            self.__gameObject[go.id] = newGameObject

        position = transform.worldPosition
        CGF.loadGameObject(supplySpawnComponent.prefabPath, go.spaceID, position, setGO)

    @onRemovedQuery(CGF.GameObject, SupplySpawnComponent)
    def onRemovedSupplyComponent(self, go, _):
        animComponent = self.__gameObject.pop(go.id).findComponentByType(AnimatorComponent)
        if animComponent is not None:
            duration = animComponent.getDuration()
            animComponent.start()
            go.createComponent(RemoveGoDelayedComponent, duration)
        return
