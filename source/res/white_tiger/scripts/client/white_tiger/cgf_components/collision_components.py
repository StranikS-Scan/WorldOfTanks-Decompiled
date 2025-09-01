# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/cgf_components/collision_components.py
import logging
from functools import partial
import BigWorld
import CGF
import GenericComponents
import Math
from white_tiger_common.wt_constants import ARENA_BONUS_TYPE_CAPS
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import onAddedQuery, onProcessQuery
from vehicle_systems.tankStructure import ColliderTypes
_logger = logging.getLogger(__name__)

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
class WTProjectileTarget(object):
    effectPath = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Effect Path', value='')
    parentGO = ComponentProperty(type=CGFMetaTypes.LINK, editorName='ParentGO', value=CGF.GameObject)


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


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.WHITE_TIGER, CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor)
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
        if not dynamicCollision:
            _logger.warning('Unable to find DynamicCollisionComponent in Game object name=%s, id=%s', gameObject.name, gameObject.id)
            return
        collision = gameObject.createComponent(BigWorld.CollisionComponent, resourceRefs['dynamicCollision'])
        payload = ((0, dynamicCollision.matrix),)
        collision.connect(dynamicCollision.ownerID, ColliderTypes.HANGAR_VEHICLE_COLLIDER if dynamicCollision.ignore else ColliderTypes.DYNAMIC_COLLIDER, payload)
        if vehicle and hasattr(vehicle, 'appearance'):
            BigWorld.wgAddIgnoredCollisionEntity(vehicle, collision, True)
