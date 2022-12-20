# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/collision_component.py
import functools
import logging
import Math
import BigWorld
import CGF
from cgf_script.component_meta_class import CGFComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery, onProcessQuery, autoregister, onRemovedQuery
import GenericComponents
from vehicle_systems.tankStructure import ColliderTypes
_logger = logging.getLogger(__name__)

class SingleCollisionComponent(CGFComponent):
    editorTitle = 'Single Collision'
    category = 'Common'
    asset = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Asset', annotations={'path': '*.model'})
    matrix = Math.Matrix()

    def __init__(self):
        super(SingleCollisionComponent, self).__init__()
        self.matrix = Math.Matrix()
        self.matrix.setIdentity()


@autoregister(presentInAllWorlds=True, presentInEditor=True)
class CollisionComponentManager(CGF.ComponentManager):

    @onAddedQuery(SingleCollisionComponent, CGF.GameObject)
    def onAdded(self, singleCollision, go):
        if not singleCollision.asset:
            _logger.warning('Single Collision component with empty asset in gameObject id=%d', go.id)
            return
        collisionAssembler = BigWorld.CollisionAssembler(((0, singleCollision.asset),), self.spaceID)
        collisionAssembler.name = 'collision'
        BigWorld.loadResourceListBG((collisionAssembler,), functools.partial(self.__onLoaded, go))

    @onRemovedQuery(SingleCollisionComponent, CGF.GameObject)
    def onRemoved(self, singleCollision, go):
        if not singleCollision.asset:
            return
        go.removeComponentByType(BigWorld.CollisionComponent)

    def __onLoaded(self, go, resources):
        if not go.isValid():
            return
        collision = go.createComponent(BigWorld.CollisionComponent, resources['collision'])
        if not collision:
            _logger.error('Cant create CollisionComponent for gameObject id=%d', go.id)
            return
        collisionData = ((0, go.findComponentByType(SingleCollisionComponent).matrix),)
        collision.connect(go.id, ColliderTypes.DYNAMIC_COLLIDER, collisionData)

    @onProcessQuery(SingleCollisionComponent, GenericComponents.TransformComponent)
    def syncTransforms(self, singleCollision, transform):
        singleCollision.matrix.set(transform.worldTransform)
