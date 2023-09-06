# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DualAccuracy.py
import typing
import BigWorld
import Event
from constants import DUAL_ACCURACY_STATE
from PlayerEvents import g_playerEvents
_DEFAULT_ACCURACY_FACTOR = 1.0

def getPlayerVehicleDualAccuracy():
    vehicle = BigWorld.player().getVehicleAttached()
    return vehicle.dynamicComponents.get('dualAccuracy', None) if vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive() else None


class DualAccuracy(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(DualAccuracy, self).__init__()
        self.__appearanceInited = False
        self.__dualAccuracyFactor = _DEFAULT_ACCURACY_FACTOR
        self.__eManager = Event.EventManager()
        self.onSetDualAccState = Event.Event(self.__eManager)
        self.__initDualAccuracyAppearance()
        self.__initDualAccuracyAvatar()

    def isActive(self):
        return self.state == DUAL_ACCURACY_STATE.ACTIVE

    def getDualAccuracyFactor(self):
        return self.__dualAccuracyFactor

    def getCurrentDualAccuracyFactor(self):
        return self.__dualAccuracyFactor if self.isActive() else _DEFAULT_ACCURACY_FACTOR

    def set_state(self, _=None):
        if self.__isAvatarReady():
            self.__updateDualAccuracyAvatar()
        if self.__appearanceInited and self.__isAppearanceReady():
            self.__updateDualAccuracyState()

    def onDestroy(self):
        self.entity.onAppearanceReady -= self.__onAppearanceReady
        self.__appearanceInited = False
        self.__eManager.clear()

    def onLeaveWorld(self):
        self.onDestroy()

    def onSiegeStateUpdated(self, typeDescriptor):
        if not self.__appearanceInited:
            return
        self.__collectDualAccuracyParams(typeDescriptor)
        self.__updateDualAccuracyAvatar()

    def __isAvatarReady(self):
        player = BigWorld.player()
        return player is not None and player.userSeesWorld()

    def __isAppearanceReady(self):
        typeDescriptor = self.entity.typeDescriptor
        if typeDescriptor is None or typeDescriptor.type.compactDescr != self.vehTypeCD:
            return False
        else:
            player = BigWorld.player()
            if player is None or player.isDisableRespawnMode:
                return False
            appearance = self.entity.appearance
            return appearance is not None and appearance.isConstructed

    def __isPlayerVehicle(self, player=None):
        player = player or BigWorld.player()
        return player is not None and player.playerVehicleID == self.entity.id

    def __onAvatarReady(self):
        self.__updateDualAccuracyAvatar()

    def __onAppearanceReady(self):
        if self.__appearanceInited:
            return
        self.__collectDualAccuracyParams()
        self.__updateDualAccuracyState()
        self.__appearanceInited = True

    def __collectDualAccuracyParams(self, typeDescriptor=None):
        typeDescriptor = typeDescriptor or self.entity.typeDescriptor
        params = typeDescriptor.gun
        self.__dualAccuracyFactor = params.dualAccuracy.afterShotDispersionAngle / params.shotDispersionAngle

    def __initDualAccuracyAvatar(self):
        if self.__isAvatarReady():
            self.__onAvatarReady()
        else:
            g_playerEvents.onAvatarReady += self.__onAvatarReady

    def __initDualAccuracyAppearance(self):
        if self.__isAppearanceReady():
            self.__onAppearanceReady()
        else:
            self.entity.onAppearanceReady += self.__onAppearanceReady

    def __updateDualAccuracyAvatar(self):
        player = BigWorld.player()
        if self.__isPlayerVehicle(player):
            player.getOwnVehicleShotDispersionAngle(player.gunRotator.turretRotationSpeed)

    def __updateDualAccuracyState(self):
        self.onSetDualAccState(self.isActive())
