# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/collisions.py
from functools import partial
import BigWorld
import CGF
import GameLogicComponents
import GenericComponents
import Math
from cgf_script.component_meta_class import CGFComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery, onProcessQuery, registerManager, Rule, autoregister
from vehicle_systems.tankStructure import ColliderTypes

def _getEntity(gameObject):
    hierarchy = CGF.HierarchyManager(gameObject.spaceID)
    parent = hierarchy.getTopMostParent(gameObject)
    entitySync = parent.findComponentByType(GenericComponents.EntityGOSync)
    return entitySync.entity if entitySync is not None else None


class DynamicCollisionComponent(CGFComponent):
    asset = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Asset', value='', annotations={'path': '*.model'})
    ownerID = ComponentProperty(type=CGFMetaTypes.INT, editorName='OwnerID', value=0)
    ignore = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Ignored by Aim', value=False)
    matrix = Math.Matrix()

    def __init__(self):
        super(DynamicCollisionComponent, self).__init__()
        self.matrix = Math.Matrix()
        self.matrix.setIdentity()


@autoregister(presentInAllWorlds=True)
class CollisionComponentManager(CGF.ComponentManager):

    @onAddedQuery(DynamicCollisionComponent, GenericComponents.TransformComponent, CGF.GameObject)
    def onAdded(self, collision, _, gameObject):
        if not collision.asset or gameObject.findComponentByType(BigWorld.CollisionComponent) is not None:
            return
        else:
            vehicle = _getEntity(gameObject)
            if vehicle is not None:
                collision.ownerID = vehicle.id
            collisionAssembler = BigWorld.CollisionAssembler(((0, collision.asset),), self.spaceID)
            collisionAssembler.name = 'dynamicCollision'
            BigWorld.loadResourceListBG((collisionAssembler,), partial(self.__onResourcesLoaded, gameObject))
            return

    @onProcessQuery(DynamicCollisionComponent, GenericComponents.TransformComponent)
    def onProcess(self, collision, transform):
        collision.matrix.set(transform.worldTransform)

    def __onResourcesLoaded(self, gameObject, resourceRefs):
        if not gameObject.isValid():
            return
        if 'dynamicCollision' in resourceRefs.failedIDs:
            return
        dynamicCollision = gameObject.findComponentByType(DynamicCollisionComponent)
        collision = gameObject.createComponent(BigWorld.CollisionComponent, resourceRefs['dynamicCollision'])
        payload = ((0, dynamicCollision.matrix),)
        collision.connect(dynamicCollision.ownerID, ColliderTypes.HANGAR_VEHICLE_COLLIDER if dynamicCollision.ignore else ColliderTypes.DYNAMIC_COLLIDER, payload)


class ProjectileTargetRegistrar(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, GameLogicComponents.ProjectileTarget, DynamicCollisionComponent)
    def onAdded(self, gameObject, target, collision):
        vehicle = _getEntity(gameObject)
        if vehicle is not None:
            target.ownerID = collision.ownerID = vehicle.id
            target.resourceID = collision.asset.replace('.model', '.havok')
        return


class DSCollisionRule(Rule):
    category = 'GameLogic'

    @registerManager(CollisionComponentManager)
    def reg1(self):
        return None

    @registerManager(ProjectileTargetRegistrar)
    def reg2(self):
        return None
