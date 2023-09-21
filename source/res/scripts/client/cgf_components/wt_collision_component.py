# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/wt_collision_component.py
from functools import partial
import BigWorld
import CGF
import GenericComponents
import Math
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onProcessQuery, registerManager, Rule, registerRule
from vehicle_systems.tankStructure import ColliderTypes

def _getEntity(gameObject):
    hierarchy = CGF.HierarchyManager(gameObject.spaceID)
    parent = hierarchy.getTopMostParent(gameObject)
    entitySync = parent.findComponentByType(GenericComponents.EntityGOSync)
    try:
        return entitySync.entity
    except TypeError:
        pass

    return None


@registerComponent
class DynamicCollisionComponent(object):
    asset = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Asset', value='', annotations={'path': '*.model'})
    ownerID = ComponentProperty(type=CGFMetaTypes.INT, editorName='OwnerID', value=0)
    ignore = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Ignored by Aim', value=False)
    matrix = Math.Matrix()

    def __init__(self):
        super(DynamicCollisionComponent, self).__init__()
        self.matrix = Math.Matrix()
        self.matrix.setIdentity()


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
            BigWorld.loadResourceListBG((collisionAssembler,), partial(self.__onResourcesLoaded, gameObject, vehicle))
            return

    @onProcessQuery(DynamicCollisionComponent, GenericComponents.TransformComponent)
    def onProcess(self, collision, transform):
        collision.matrix.set(transform.worldTransform)

    def __onResourcesLoaded(self, gameObject, vehicle, resourceRefs):
        if not gameObject.isValid():
            return
        if 'dynamicCollision' in resourceRefs.failedIDs:
            return
        dynamicCollision = gameObject.findComponentByType(DynamicCollisionComponent)
        collision = gameObject.createComponent(BigWorld.CollisionComponent, resourceRefs['dynamicCollision'])
        payload = ((0, dynamicCollision.matrix),)
        collision.connect(dynamicCollision.ownerID, ColliderTypes.HANGAR_VEHICLE_COLLIDER if dynamicCollision.ignore else ColliderTypes.DYNAMIC_COLLIDER, payload)
        if vehicle and hasattr(vehicle, 'appearance'):
            BigWorld.wgAddIgnoredCollisionEntity(vehicle, collision)


class ProjectileTargetRegistrar(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, GenericComponents.ProjectileTarget, DynamicCollisionComponent)
    def onAdded(self, gameObject, target, collision):
        vehicle = _getEntity(gameObject)
        if vehicle is not None:
            target.ownerID = collision.ownerID = vehicle.id
            target.resourceID = collision.asset.replace('.model', '.havok')
        return


@registerRule
class DSCollisionRule(Rule):
    category = 'GameLogic'

    @registerManager(CollisionComponentManager)
    def reg1(self):
        return None

    @registerManager(ProjectileTargetRegistrar)
    def reg2(self):
        return None
