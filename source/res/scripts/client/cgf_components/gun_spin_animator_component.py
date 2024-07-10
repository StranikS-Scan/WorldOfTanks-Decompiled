# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/gun_spin_animator_component.py
import math
import typing
import CGF
import GenericComponents
import Math
from constants import IS_CLIENT
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery, onProcessQuery
from events_handler import eventHandler
from vehicle_systems.cgf_helpers import getVehicleEntityComponentByGameObject
from Vehicular import GunEffectsController
if IS_CLIENT:
    from SpinGunController import SpinGunController
    from vehicle_systems.spin_guns.system_interfaces import IGunSpinningListener
else:

    class SpinGunController(object):
        pass


    class IGunSpinningListener(object):
        pass


if typing.TYPE_CHECKING:
    from vehicle_systems.spin_guns.system_interfaces import IGunSpinningEvents
MATH_2PI = math.pi * 2

@registerComponent
class GunSpinAnimator(IGunSpinningListener):
    editorTitle = 'Gun Spin Animator'
    category = 'Auto Shoot Guns'
    maxRPM = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Max RPM', value=600.0)
    barrelsCount = ComponentProperty(type=CGFMetaTypes.INT, editorName='Barrels count', value=8)
    timeToStop = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Time to stop', value=0.5)

    def __init__(self):
        self.angularVelocity = 0.0
        self.angularAcceleration = 0.0
        self.__isControlledByClient = True

    def isControlledByClient(self):
        return self.__isControlledByClient

    @eventHandler
    def onSpinFactorUpdate(self, spinFactor):
        self.angularVelocity = spinFactor * self.maxRPM * MATH_2PI / 60.0

    @eventHandler
    def onSpinningActivation(self):
        self.__isControlledByClient = False
        self.angularAcceleration = 0.0

    @eventHandler
    def onSpinningDeactivation(self):
        self.__isControlledByClient = True
        self.angularAcceleration = -self.angularVelocity / self.timeToStop

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
    def onGunSpinAnimatorAdded(self, gameObject, gunSpinAnimator):
        ctrl = getVehicleEntityComponentByGameObject(gameObject, SpinGunController)
        if ctrl is not None and ctrl.spinningEvents is not None:
            events = ctrl.spinningEvents
            events.onSpinFactorUpdate.lateAdd(gunSpinAnimator.onSpinFactorUpdate)
            events.onSpinningActivation.lateAdd(gunSpinAnimator.onSpinningActivation)
            events.onSpinningDeactivation += gunSpinAnimator.onSpinningDeactivation
        return

    @onRemovedQuery(CGF.GameObject, GunSpinAnimator)
    def onGunSpinAnimatorRemoved(self, gameObject, gunSpinAnimator):
        ctrl = getVehicleEntityComponentByGameObject(gameObject, SpinGunController)
        if ctrl is not None and ctrl.spinningEvents is not None:
            events = ctrl.spinningEvents
            events.onSpinningDeactivation -= gunSpinAnimator.onSpinningDeactivation
            events.onSpinningActivation -= gunSpinAnimator.onSpinningActivation
            events.onSpinFactorUpdate -= gunSpinAnimator.onSpinFactorUpdate
        return

    @onAddedQuery(CGF.GameObject, GunEffectsController, tickGroup='PreSimulation')
    def onGunEffectsControllerAdded(self, gameObject, gunEffectsController):
        ctrl = getVehicleEntityComponentByGameObject(gameObject, SpinGunController)
        if ctrl is not None and ctrl.spinningEvents is not None:
            events = ctrl.spinningEvents
            events.onSpinningActivation.lateAdd(gunEffectsController.startSpin)
            events.onSpinningDeactivation += gunEffectsController.stopSpin
        return

    @onRemovedQuery(CGF.GameObject, GunEffectsController)
    def onGunEffectsControllerRemoved(self, gameObject, gunEffectsController):
        ctrl = getVehicleEntityComponentByGameObject(gameObject, SpinGunController)
        if ctrl is not None and ctrl.spinningEvents is not None:
            events = ctrl.spinningEvents
            events.onSpinningActivation -= gunEffectsController.startSpin
            events.onSpinningDeactivation -= gunEffectsController.stopSpin
        return

    @onProcessQuery(SpinGunController)
    def onControllerTick(self, controller):
        if controller is not None and controller.spinningEvents is not None:
            controller.spinningEvents.processTick()
        return

    @onProcessQuery(GunSpinAnimator, GenericComponents.TransformComponent)
    def onAnimatorTick(self, component, transform):
        dt = self.clock.gameDelta
        currentAngle = transform.rotationYPR.z
        if not component.isControlledByClient():
            deltaAngle = component.angularVelocity * dt
            transform.rotationYPR = Math.Vector3(0, 0, (currentAngle + deltaAngle) % MATH_2PI)
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
            transform.rotationYPR = Math.Vector3(0, 0, finalAngle)
            return
        component.angularVelocity += component.angularAcceleration * dt
        transform.rotationYPR = Math.Vector3(0, 0, (currentAngle + deltaAngle) % MATH_2PI)
