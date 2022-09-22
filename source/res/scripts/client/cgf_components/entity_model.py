# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/entity_model.py
import BigWorld
import CGF
import GenericComponents
import Math
from cgf_script.component_meta_class import CGFComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, registerManager, Rule
from math_utils import createSRTMatrix

def _getEntity(gameObject):
    hierarchy = CGF.HierarchyManager(gameObject.spaceID)
    parent = hierarchy.getTopMostParent(gameObject)
    entitySync = parent.findComponentByType(GenericComponents.EntityGOSync)
    try:
        return entitySync.entity
    except TypeError:
        pass

    return None


class EntityPickerTarget(CGFComponent):
    width = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Width', value=1.0)
    height = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Height', value=1.0)
    depth = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Depth', value=1.0)


class EntityPickerTargetManager(CGF.ComponentManager):

    @onAddedQuery(EntityPickerTarget, CGF.GameObject)
    def onAdded(self, target, gameObject):
        entity = _getEntity(gameObject)
        if entity is not None:
            entityMatrix = Math.Matrix(entity.matrix)
            model = BigWorld.Model('')
            model.addMotor(BigWorld.Servo(createSRTMatrix((target.width, target.height, target.depth), (entityMatrix.yaw, entityMatrix.pitch, entityMatrix.roll), entityMatrix.translation)))
            entity.model = model
            entity.targetCaps = [1]
            entity.targetFullBound = True
        return

    @onRemovedQuery(EntityPickerTarget, CGF.GameObject)
    def onRemoved(self, _, gameObject):
        entity = _getEntity(gameObject)
        if entity is not None and hasattr(entity, 'model'):
            entity.model = None
        return


class EntityPickerTargetRule(Rule):
    category = 'GameLogic'

    @registerManager(EntityPickerTargetManager)
    def reg(self):
        return None
