# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/gun_spin_animator_component.py
import math
import CGF
import GenericComponents
import Math
from constants import IS_CLIENT
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery, onProcessQuery
if IS_CLIENT:
    from SpinGunController import SpinGunController
else:

    class SpinGunController(object):
        pass


MATH_2PI = math.pi * 2

@registerComponent
class GunSpinAnimator(object):
    editorTitle = 'Gun Spin Animator'
    category = 'Auto Shoot Guns'
    maxRPM = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Max RPM', value=600.0)
    barrelsCount = ComponentProperty(type=CGFMetaTypes.INT, editorName='Barrels count', value=8)
    timeToStop = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Time to stop', value=0.5)

    def __init__(self):
        self.angularVelocity = 0.0
        self.angularAcceleration = 0.0
        self.__isControlledByClient = True

    def setSpinFactor(self, factor):
        self.angularVelocity = factor * self.maxRPM * MATH_2PI / 60.0

    def isControlledByClient(self):
        return self.__isControlledByClient

    def enableClientControll(self):
        self.__isControlledByClient = True
        self.angularAcceleration = -self.angularVelocity / self.timeToStop

    def disableClientControll(self):
        self.__isControlledByClient = False
        self.angularAcceleration = 0.0

    def calculateDelta(self, dt):
        return self.angularVelocity * dt + self.angularAcceleration * dt * dt / 2

    def angleToBarrelAngle(self, angle):
        angle %= MATH_2PI
        if self.barrelsCount == 0:
            return angle
        angle /= MATH_2PI
        angle *= self.barrelsCount
        angle = int(angle)
        angle *= MATH_2PI / self.barrelsCount
        return angle


@autoregister(presentInAllWorlds=True)
class SpinningGunManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, GunSpinAnimator)
    def onGunSpinAnimatorAdded(self, go, gunSpinAnimator):
        hierarchy = CGF.HierarchyManager(go.spaceID)
        root = hierarchy.getTopMostParent(go)
        controller = root.findComponentByType(SpinGunController)
        if controller is not None:
            controller.spinningAnimator.addSpinAnimator(gunSpinAnimator)
        return

    @onRemovedQuery(CGF.GameObject, GunSpinAnimator)
    def onGunSpinAnimatorRemoved(self, go, gunSpinAnimator):
        hierarchy = CGF.HierarchyManager(go.spaceID)
        root = hierarchy.getTopMostParent(go)
        controller = root.findComponentByType(SpinGunController)
        if controller is not None:
            controller.spinningAnimator.removeSpinAnimator(gunSpinAnimator)
        return

    @onProcessQuery(SpinGunController)
    def onControllerTick(self, controller):
        if controller is not None and controller.spinningAnimator is not None:
            controller.spinningAnimator.updateSpinAnimators()
        return

    @onProcessQuery(GunSpinAnimator, GenericComponents.TransformComponent)
    def onAnimatorTick(self, component, transform):
        dt = self.clock.gameDelta
        currentAngle = transform.rotation.z
        if not component.isControlledByClient():
            deltaAngle = component.angularVelocity * dt
            transform.rotation = Math.Vector3(0, 0, (currentAngle + deltaAngle) % MATH_2PI)
            return
        if component.angularVelocity == 0.0 or component.angularAcceleration == 0.0:
            return
        remainingTime = -component.angularVelocity / component.angularAcceleration
        remainingSpin = component.calculateDelta(remainingTime)
        finalAngle = component.angleToBarrelAngle(currentAngle + remainingSpin)
        deltaAngle = component.calculateDelta(dt)
        if remainingTime < dt or abs(remainingSpin) < MATH_2PI / component.barrelsCount and abs(deltaAngle) % MATH_2PI > abs(finalAngle - currentAngle) % MATH_2PI:
            component.angularVelocity = 0.0
            component.angularAcceleration = 0.0
            transform.rotation = Math.Vector3(0, 0, finalAngle)
            return
        component.angularVelocity += component.angularAcceleration * dt
        transform.rotation = Math.Vector3(0, 0, (currentAngle + deltaAngle) % MATH_2PI)
