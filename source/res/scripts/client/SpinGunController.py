# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SpinGunController.py
import logging
import typing
import weakref
import BigWorld
from auto_shoot_guns.auto_shoot_guns_common import SpinGunState
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_helpers import getGunSoundObject
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_wrappers import checkStateStatus
_logger = logging.getLogger(__name__)
_MAX_SPIN_VALUE = 1.0

def getPlayerVehicleSpinGunController():
    vehicle = BigWorld.player().getVehicleAttached()
    return vehicle.dynamicComponents.get('spinGunController', None) if vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive() else None


class SpinGunSpinningAnimator(object):

    def __init__(self, vehicle, controller):
        super(SpinGunSpinningAnimator, self).__init__()
        self.__vehicle = weakref.proxy(vehicle)
        self.__controller = weakref.proxy(controller)
        self.__activationSound = self.__deactivationSound = ''
        self.__spinAnimators = set()
        self.__isActive = False

    def initSoundParams(self, isPlayerVehicle, activationSounds, deactivationSounds):
        self.__activationSound = activationSounds.getEvents()[0 if isPlayerVehicle else 1]
        self.__deactivationSound = deactivationSounds.getEvents()[0 if isPlayerVehicle else 1]

    def destroy(self):
        self.__vehicle = None
        self.__controller = None
        self.__spinAnimators.clear()
        self.__activationSound = self.__deactivationSound = ''
        return

    def addSpinAnimator(self, spinAnimator):
        self.__spinAnimators.add(spinAnimator)
        if self.__isActive:
            spinAnimator.setSpinFactor(self.__controller.getSpinningValue())
            spinAnimator.disableClientControll()

    def removeSpinAnimator(self, spinAnimator):
        self.__spinAnimators.discard(spinAnimator)

    def updateSpinAnimators(self):
        for animator in self.__spinAnimators if self.__isActive else ():
            animator.setSpinFactor(self.__controller.getSpinningValue())

    def updateSpinningStatus(self, stateStatus):
        isActive = stateStatus is not None and stateStatus.state != SpinGunState.NOT_STARTED
        if self.__isActive != isActive:
            spinFactor = self.__controller.getSpinningValue()
            self.__updateSpinAnimators(isActive, spinFactor, self.__controller.getSpinningMinValue())
            self.__playGunObjectSound(self.__activationSound if isActive else self.__deactivationSound)
        self.__isActive = isActive
        return

    def __playGunObjectSound(self, soundName):
        if soundName:
            getGunSoundObject(self.__vehicle).play(soundName)

    def __updateSpinAnimators(self, isActive, spinFactor, minSpinFactor):
        for animator in self.__spinAnimators:
            if isActive:
                animator.disableClientControll()
                animator.setSpinFactor(spinFactor)
            if not animator.isControlledByClient():
                animator.setSpinFactor(minSpinFactor)
                animator.enableClientControll()


class SpinGunController(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(SpinGunController, self).__init__()
        self.__appearanceInited = False
        self.__spinningAnimator = SpinGunSpinningAnimator(self.entity, self)
        self.__maxValue = _MAX_SPIN_VALUE
        self.__minValue = self.__downSpeed = self.__upSpeed = 0.0
        self.__initSpinningAppearance()

    @property
    def spinningAnimator(self):
        return self.__spinningAnimator

    def isSpinActive(self):
        return self.stateStatus is not None and self.stateStatus.state in SpinGunState.ACTIVE_STATES

    @checkStateStatus(states=SpinGunState.ACTIVE_STATES, defReturn=0.0)
    def getSpinningValue(self, stateStatus=None):
        if stateStatus.state not in SpinGunState.DYNAMIC_STATES:
            return stateStatus.spinFactor
        dt = max(BigWorld.serverTime() - stateStatus.stateActivationTime, 0.0)
        return min(stateStatus.spinFactor + dt * self.__upSpeed, self.__maxValue) if stateStatus.state == SpinGunState.SPIN_UP else max(stateStatus.spinFactor - dt * self.__downSpeed, self.__minValue)

    def getSpinningMinValue(self):
        return self.__minValue

    def set_stateStatus(self, _=None):
        if self.__appearanceInited and self.__isAppearanceReady():
            self.__updateSpinningAppearance()

    def onDestroy(self):
        self.entity.onAppearanceReady -= self.__onAppearanceReady
        self.__spinningAnimator.destroy()
        self.__appearanceInited = False

    def onLeaveWorld(self):
        self.onDestroy()

    def __isAppearanceReady(self):
        appearance = self.entity.appearance
        return appearance is not None and appearance.isConstructed

    def __isPlayerVehicle(self, player=None):
        player = player or BigWorld.player()
        return player is not None and player.playerVehicleID == self.entity.id

    def __onAppearanceReady(self):
        if self.__appearanceInited:
            return
        params = self.entity.typeDescriptor.gun
        self.__minValue, self.__maxValue = params.spin.startFactor, _MAX_SPIN_VALUE
        self.__downSpeed = (self.__maxValue - self.__minValue) / params.spin.spinDownTimeout
        self.__upSpeed = (self.__maxValue - self.__minValue) / params.spin.spinUpTimeout
        self.__spinningAnimator.initSoundParams(self.entity.isPlayerVehicle, params.spinEffect.activationSound, params.spinEffect.deactivationSound)
        self.__updateSpinningAppearance()
        self.__appearanceInited = True

    def __initSpinningAppearance(self):
        if self.__isAppearanceReady():
            self.__onAppearanceReady()
        else:
            self.entity.onAppearanceReady += self.__onAppearanceReady

    def __updateSpinningAppearance(self):
        self.__spinningAnimator.updateSpinningStatus(self.stateStatus)
