# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTShieldImpact.py
import BigWorld
import CGF
import GenericComponents
import Math
import logging
from script_component.DynamicScriptComponent import DynamicScriptComponent
from constants import IS_VS_EDITOR
if not IS_VS_EDITOR:
    from white_tiger.cgf_components.collision_components import WTProjectileTarget
    from VehicleEffects import DamageFromShotDecoder
_logger = logging.getLogger(__name__)

class WTShieldImpact(DynamicScriptComponent):

    def __init__(self):
        super(WTShieldImpact, self).__init__()
        self.entity.onShowDamageFromShot += self.showShieldCollisionVFX

    def showShieldCollisionVFX(self, attackerID, points, effectsIndex, damageFactor, lastMaterialIsShield):
        if not self.shieldActive:
            return
        parsedHitPoints = DamageFromShotDecoder.parseHitPoints(points, self.entity.appearance.collisions)
        firstHitPoint = parsedHitPoints[0]
        compoundModel = self.entity.appearance.compoundModel
        compMatrix = Math.Matrix(compoundModel.node(firstHitPoint.componentName))
        firstHitDirLocal = firstHitPoint.matrix.applyToAxis(2)
        firstHitDir = compMatrix.applyVector(firstHitDirLocal)
        worldHitPoint = compMatrix.applyPoint(firstHitPoint.matrix.translation)
        trace = BigWorld.wg_collideDynamics(BigWorld.player().spaceID, worldHitPoint - firstHitDir * 10, worldHitPoint, [self.entity.id])
        if not trace:
            _logger.debug('Trace not intersecting the shield!')
            return
        hierarchy = CGF.HierarchyManager(self.entity.spaceID)
        compList = hierarchy.findComponentsInHierarchy(self.entity.entityGameObject, WTProjectileTarget)
        if not compList:
            _logger.error('Could not find any WTProjectileTarget on GameObject!')
            return
        targetGO = compList[0][0]
        targetComp = compList[0][1]
        tComp = targetGO.findComponentByType(GenericComponents.TransformComponent)
        if not targetComp or not tComp:
            _logger.error('Could not find WTProjectileTarget or TransformComponent on GameObject!')
            return
        worldTransform = tComp.worldTransform
        worldTransform.invert()
        localTransform = Math.Matrix()
        localTransform.setRotateYPR(Math.Vector3(trace[1].yaw, trace[1].pitch, 0.0))
        localTransform.translation = trace[6]
        localTransform.postMultiply(worldTransform)
        CGF.loadGameObjectIntoHierarchy(targetComp.effectPath, targetGO, localTransform)
