# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/entity_components/vehicle_mechanic_component.py
import typing
from functools import wraps
import BigWorld
from PlayerEvents import g_playerEvents

def ifPlayerVehicle(method):

    @wraps(method)
    def wrapper(mechanicComponent, *args, **kwargs):
        player = BigWorld.player()
        if mechanicComponent.isPlayerVehicle(player):
            method(mechanicComponent, player, *args, **kwargs)

    return wrapper


def getPlayerVehicleMechanic(mechanicName):
    vehicle = BigWorld.player().getVehicleAttached()
    return vehicle.dynamicComponents.get(mechanicName, None) if vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive() else None


class VehicleMechanicComponent(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(VehicleMechanicComponent, self).__init__()
        self.__componentDestroyed = False
        self.__appearanceInited = False

    def isComponentDestroyed(self):
        return self.__componentDestroyed

    def isPlayerVehicle(self, player):
        return self.__isAvatarReady(player) and self.entity.id == player.playerVehicleID

    def onDestroy(self):
        if self.__componentDestroyed:
            return
        self.entity.onAppearanceReady -= self.__onAppearanceReady
        self.__appearanceInited = False
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        self.__componentDestroyed = True

    def onLeaveWorld(self):
        self.onDestroy()

    def onSiegeStateUpdated(self, typeDescriptor):
        if not self.__appearanceInited:
            return
        self._onSiegeStateUpdate(typeDescriptor)
        self._updateMechanicAvatar()

    def _initMechanic(self):
        self.__initMechanicAppearance()
        self.__initMechanicAvatar()

    def _onAppearanceReady(self):
        pass

    def _onMechanicAvatarUpdate(self, player):
        pass

    def _onMechanicAppearanceUpdate(self):
        pass

    def _onSiegeStateUpdate(self, typeDescriptor):
        pass

    @ifPlayerVehicle
    def _updateMechanicAvatar(self, player=None):
        self._onMechanicAvatarUpdate(player)

    def _updateMechanicAppearance(self):
        if self.__appearanceInited and self.__isAppearanceReady():
            self._onMechanicAppearanceUpdate()

    def __initMechanicAvatar(self):
        if self.__isAvatarReady():
            self.__onAvatarReady()
        else:
            g_playerEvents.onAvatarReady += self.__onAvatarReady

    def __initMechanicAppearance(self):
        if self.__isAppearanceReady():
            self.__onAppearanceReady()
        else:
            self.entity.onAppearanceReady += self.__onAppearanceReady

    def __isAvatarReady(self, player=None):
        player = player or BigWorld.player()
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
            return appearance is not None and appearance.isConstructed and not appearance.isDestroyed

    def __onAvatarReady(self):
        self._updateMechanicAvatar()

    def __onAppearanceReady(self):
        if self.__appearanceInited:
            return
        self._onAppearanceReady()
        self._onMechanicAppearanceUpdate()
        self.__appearanceInited = True
