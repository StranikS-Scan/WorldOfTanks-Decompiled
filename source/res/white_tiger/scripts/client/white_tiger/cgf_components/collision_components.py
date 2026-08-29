# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/cgf_components/collision_components.py
from __future__ import absolute_import
import logging
from functools import partial
import BigWorld
import CGF
import GenericComponents
import Math
from cgf_script.registration import ComponentProperty, registerComponent
from vehicle_systems.tankStructure import ColliderTypes
_logger = logging.getLogger(__name__)

@registerComponent
class WTProjectileTarget(object):
    effectPath = ComponentProperty(type=CGF.PropertyType.String, editorName='Effect Path', value='')
    parentGO = ComponentProperty(type=CGF.PropertyType.Link, editorName='ParentGO', value=CGF.GameObject)


@registerComponent
class DynamicCollisionComponent(object):
    asset = ComponentProperty(type=CGF.PropertyType.String, editorName='Asset', value='', annotations={'path': '*.model'})
    ownerID = ComponentProperty(type=CGF.PropertyType.Int, editorName='OwnerID', value=0)
    ignore = ComponentProperty(type=CGF.PropertyType.Bool, editorName='Ignored by Aim', value=False)
    matrix = Math.Matrix()

    def __init__(self):
        super(DynamicCollisionComponent, self).__init__()
        self.matrix = Math.Matrix()
        self.matrix.setIdentity()


class CollisionSystem(CGF.System):
    DynCollisionActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(DynamicCollisionComponent), CGF.Has(CGF.TransformComponent))
    CollisionActivated = CGF.ActivateReaction(CGF.ReactRw(BigWorld.CollisionComponent), CGF.Rw(DynamicCollisionComponent), CGF.Ro(CGF.TransformComponent))
    DynCollisionIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.Rw(DynamicCollisionComponent), CGF.Ro(CGF.TransformComponent))
    CollisionAccess = CGF.AccessReaction(CGF.Ro(BigWorld.CollisionComponent))
    EntitySyncAccess = CGF.AccessReaction(CGF.Rw(GenericComponents.EntityGOSync))
    DynCollisionAccess = CGF.AccessReaction(CGF.Rw(DynamicCollisionComponent))
    Reactions = CGF.Reactions(DynCollisionActivated, CollisionActivated, DynCollisionIterate, CollisionAccess, EntitySyncAccess, DynCollisionAccess)

    def update(self):
        collisionAccess = self.reaction(self.CollisionAccess)
        entitySyncAccess = self.reaction(self.EntitySyncAccess)
        for gameObject, collision in self.reaction(self.DynCollisionActivated):
            self.onAdded(collision, gameObject, collisionAccess, entitySyncAccess)

        for collision, dynCollision, transform in self.reaction(self.CollisionActivated):
            self.onCollisionActivated(collision, dynCollision, transform)

        for collision, transform in self.reaction(self.DynCollisionIterate):
            self.onProcess(collision, transform)

    def onAdded(self, collision, gameObject, collisionAccess, entitySyncAccess):
        if not collision.asset or collisionAccess.find(gameObject) is not None:
            return
        else:
            vehicle = self._getEntity(gameObject, entitySyncAccess)
            if vehicle is not None:
                collision.ownerID = vehicle.id
            else:
                _logger.warning('DynamicCollisionComponent: owner entity not found, name=%s, id=%s', gameObject.name, gameObject.id)
            collisionAssembler = BigWorld.CollisionAssembler(((0, collision.asset),), self.spaceID)
            collisionAssembler.name = 'dynamicCollision'
            BigWorld.loadResourceListBG((collisionAssembler,), partial(self.__onResourcesLoaded, gameObject))
            return

    def onCollisionActivated(self, collision, dynCollision, transform):
        if not dynCollision.asset:
            return
        else:
            dynCollision.matrix.set(transform.worldTransform)
            payload = ((0, dynCollision.matrix),)
            collision.connect(dynCollision.ownerID, ColliderTypes.HANGAR_VEHICLE_COLLIDER if dynCollision.ignore else ColliderTypes.DYNAMIC_COLLIDER, payload)
            vehicle = BigWorld.entities.get(dynCollision.ownerID)
            if vehicle is not None and hasattr(vehicle, 'appearance'):
                BigWorld.wgAddIgnoredCollisionEntity(vehicle, collision, True)
            return

    def onProcess(self, collision, transform):
        collision.matrix.set(transform.worldTransform)

    def _getEntity(self, gameObject, entitySyncAccess):
        parent = self.hierarchy.getTopMostParent(gameObject)
        entitySync = entitySyncAccess.find(parent)
        try:
            return entitySync.entity
        except TypeError:
            pass

        return None

    def __onResourcesLoaded(self, gameObject, resourceRefs):
        if not gameObject.valid:
            return
        if 'dynamicCollision' in resourceRefs.failedIDs:
            return
        dynCollisionAccess = self.reaction(self.DynCollisionAccess)
        dynamicCollision = dynCollisionAccess.find(gameObject)
        if not dynamicCollision:
            if gameObject.isActive:
                _logger.warning('Unable to find DynamicCollisionComponent in Game object name=%s, id=%s', gameObject.name, gameObject.id)
            return
        q = CGF.CommandQueue(self.gom)
        q.createComponent(gameObject, BigWorld.CollisionComponent, self.spaceID, resourceRefs['dynamicCollision'])
