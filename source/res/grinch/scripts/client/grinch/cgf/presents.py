# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/cgf/presents.py
import CGF
import Math
from GenericComponents import TransformComponent, EntityGOSync
from typing import TYPE_CHECKING
import math_utils
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery, onProcessQuery
from grinch_common.grinch_constants import ARENA_BONUS_TYPE_CAPS
if TYPE_CHECKING:
    from GrinchScoreComponent import GrinchScoreComponent
    from typing import Optional

def getScoreComponent():
    import BigWorld
    player = BigWorld.player()
    if not player or not player.arena:
        return
    else:
        arenaInfo = player.arena.arenaInfo
        return None if not arenaInfo else arenaInfo.dynamicComponents.get('GrinchScoreComponent')


@registerComponent
class PresentComponent(object):
    category = 'Grinch'
    top = ComponentProperty(type=CGFMetaTypes.LINK, editorName='topSlot', value=CGF.GameObject)
    rotationTarget = ComponentProperty(type=CGFMetaTypes.LINK, editorName='rotationTarget', value=CGF.GameObject)

    def __init__(self):
        self.parent = None
        return


@registerComponent
class PresentStackComponent(object):
    category = 'Grinch'
    appearance = ComponentProperty(type=CGFMetaTypes.LINK, editorName='appearanceLink', value=CGF.GameObject)
    base = ComponentProperty(type=CGFMetaTypes.LINK, editorName='baseGOLink', value=CGF.GameObject)

    def __init__(self):
        self.top = self.base

    def setCounter(self, go, value):
        value = max(value, 0)
        hierarchy = CGF.HierarchyManager(self.spaceID)
        for presentGO, _ in hierarchy.findComponentsInHierarchy(go, PresentComponent):
            index = int(presentGO.name.split('_')[-1])
            if index <= value:
                presentGO.activate()
            presentGO.deactivate()


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.GRINCH, CGF.DomainOption.DomainClient)
class PresentCarryManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, PresentStackComponent)
    def onAdded(self, go, presentStack):
        vehicle = self.__getVehicle(go)
        if not vehicle:
            return
        scoreComponent = getScoreComponent()
        if not scoreComponent:
            return
        points, _ = scoreComponent.getVehiclePoints(vehicle.id)
        presentStack.setCounter(go, points)

    @onProcessQuery(CGF.GameObject, PresentComponent, tickGroup='Simulation')
    def onProcess(self, go, present):
        targetTransform = present.rotationTarget.findComponentByType(TransformComponent)
        speed = 0.0
        vehicle = self.__getVehicle(go)
        if vehicle is not None and vehicle.appearance.filter is not None:
            speed = vehicle.appearance.filter.averageSpeed
        local = targetTransform.transform
        val = math_utils.clamp(-1.0, 1.0, speed / 45.0) * -0.5
        rotation = Math.Matrix()
        rotation.setRotateX(val)
        rotation.translation = local.translation
        targetTransform.transform = rotation
        return

    def __getVehicle(self, gameObject):
        hierarchy = CGF.HierarchyManager(self.spaceID)
        rootGameObject = hierarchy.getTopMostParent(gameObject)
        goSyncComponent = rootGameObject.findComponentByType(EntityGOSync)
        return None if goSyncComponent is None else goSyncComponent.entity
