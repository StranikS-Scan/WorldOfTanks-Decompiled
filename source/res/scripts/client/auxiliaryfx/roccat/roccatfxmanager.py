# Embedded file name: scripts/client/AuxiliaryFx/Roccat/RoccatFxManager.py
import BigWorld
from AuxiliaryFx.FxController import IAuxiliaryVehicleFx

class ColorState:

    def __init__(self, zone, effect, speed, color):
        self.zone = zone
        self.effect = effect
        self.speed = speed
        self.color = color


class RoccatFxManager:
    ZONE_EVENT = 1
    ZONE_AMBIENT = 2
    EFFECT_OFF = 0
    EFFECT_ON = 1
    EFFECT_BLINKING = 2
    EFFECT_BREATHING = 3
    EFFECT_HEARTBEAT = 4
    SPEED_NOCHANGE = 0
    SPEED_SLOW = 1
    SPEED_NORMAL = 2
    SPEED_FAST = 3

    def __init__(self):
        self.__roccatFx = BigWorld.WGRoccatFx
        self.__isEnabled = False
        self.__roccatFx.setOnReadyCallback(self.__onRoccatReady)
        self.__roccatFx.initialize()
        self.__tempColorCallbackId = None
        self.__mainColorState = ColorState(0, 0, 0, (0, 0, 0))
        return

    def destroy(self):
        if self.__isEnabled:
            self.resetBackground()
        self.__roccatFx.clearOnReadyCallback()
        self.__roccatFx = None
        if self.__tempColorCallbackId is not None:
            BigWorld.cancelCallback(self.__tempColorCallbackId)
        return

    def __onRoccatReady(self):
        self.__isEnabled = True
        self.resetBackground()

    def start(self):
        self.resetBackground()

    def isEnabled(self):
        return self.__isEnabled

    def setMainColors(self, zone, effect, speed, color):
        if not self.isEnabled():
            return
        self.__mainColorState = ColorState(zone, effect, speed, color)
        self.__roccatFx.setColors(zone, effect, speed, color)

    def launchTempColors(self, zone, effect, speed, color, time):
        if not self.isEnabled():
            return
        else:
            if self.__tempColorCallbackId is not None:
                BigWorld.cancelCallback(self.__tempColorCallbackId)
            self.__roccatFx.setColors(zone, effect, speed, color)
            self.__tempColorCallbackId = BigWorld.callback(time, self.__onTempColorStops)
            return

    def __onTempColorStops(self):
        self.__tempColorCallbackId = None
        self.__roccatFx.setColors(self.__mainColorState.zone, self.__mainColorState.effect, self.__mainColorState.speed, self.__mainColorState.color)
        return

    def resetBackground(self):
        self.setMainColors(RoccatFxManager.ZONE_AMBIENT, RoccatFxManager.EFFECT_ON, RoccatFxManager.SPEED_SLOW, (255, 240, 0))

    def startInvitationEffect(self):
        self.setMainColors(RoccatFxManager.ZONE_EVENT, RoccatFxManager.EFFECT_BLINKING, RoccatFxManager.SPEED_FAST, (255, 255, 255))

    def stopInvitationEffect(self):
        self.resetBackground()

    def systemMessageEffect(self):
        self.launchTempColors(RoccatFxManager.ZONE_EVENT, RoccatFxManager.EFFECT_BREATHING, RoccatFxManager.SPEED_SLOW, (0, 0, 255), 3.5)

    def channelOpenedEffect(self):
        self.launchTempColors(RoccatFxManager.ZONE_EVENT, RoccatFxManager.EFFECT_HEARTBEAT, RoccatFxManager.SPEED_SLOW, (0, 255, 255), 5)

    def startTicksEffect(self):
        self.launchTempColors(RoccatFxManager.ZONE_EVENT, RoccatFxManager.EFFECT_BREATHING, RoccatFxManager.SPEED_FAST, (255, 255, 255), 30)

    def roundStartedEffect(self):
        self.launchTempColors(RoccatFxManager.ZONE_EVENT, RoccatFxManager.EFFECT_HEARTBEAT, RoccatFxManager.SPEED_SLOW, (0, 255, 0), 2)


class RoccatVehicleFx(IAuxiliaryVehicleFx):
    HEALTH_EFFECTS = [(9000, (RoccatFxManager.ZONE_AMBIENT,
       RoccatFxManager.EFFECT_ON,
       RoccatFxManager.SPEED_NORMAL,
       (0, 255, 0))),
     (0.6, (RoccatFxManager.ZONE_AMBIENT,
       RoccatFxManager.EFFECT_ON,
       RoccatFxManager.SPEED_NORMAL,
       (255, 255, 0))),
     (0.3, (RoccatFxManager.ZONE_AMBIENT,
       RoccatFxManager.EFFECT_ON,
       RoccatFxManager.SPEED_NORMAL,
       (255, 0, 0))),
     (0, (RoccatFxManager.ZONE_AMBIENT,
       RoccatFxManager.EFFECT_ON,
       RoccatFxManager.SPEED_NORMAL,
       (255, 255, 255)))]
    DEATH_EFFECT = (RoccatFxManager.ZONE_EVENT,
     RoccatFxManager.EFFECT_BLINKING,
     RoccatFxManager.SPEED_FAST,
     (255, 0, 0),
     5)

    def __init__(self, vehicle, fxManager):
        IAuxiliaryVehicleFx.__init__(self, vehicle, fxManager)
        self.__prevHealth = vehicle.health
        effect = self.__getHealthEffect(vehicle.health, vehicle.typeDescriptor.maxHealth)
        self._fxManager.setMainColors(*effect)

    def destroy(self):
        self._fxManager.resetBackground()

    def __getHealthEffect(self, health, maxHealth):
        durability = health * 1.0 / maxHealth
        healthEffect = RoccatVehicleFx.HEALTH_EFFECTS[0][1]
        for durabilityEffect in RoccatVehicleFx.HEALTH_EFFECTS:
            if durabilityEffect[0] < durability:
                break
            healthEffect = durabilityEffect[1]

        return healthEffect

    def update(self, vehicle):
        health = vehicle.health
        if health != self.__prevHealth:
            effect = self.__getHealthEffect(health, vehicle.typeDescriptor.maxHealth)
            self._fxManager.setMainColors(*effect)
        if health <= 0:
            self._fxManager.launchTempColors(*RoccatVehicleFx.DEATH_EFFECT)
        self.__prevHealth = health
