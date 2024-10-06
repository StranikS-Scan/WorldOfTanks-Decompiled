# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/entity_components/vehicle_mechanic_component.py
import logging
import operator
import typing
from functools import wraps
import BigWorld
import CGF
from PlayerEvents import g_playerEvents
from vehicle_systems.model_assembler import loadAppearancePrefab
if typing.TYPE_CHECKING:
    from Avatar import PlayerAvatar
    from items.vehicles import VehicleDescriptor
    from Vehicle import Vehicle
_logger = logging.getLogger(__name__)

def ifAppearanceReady(method):

    @wraps(method)
    def wrapper(mechanicComponent, *args, **kwargs):
        if mechanicComponent.isAppearanceReady():
            method(mechanicComponent, *args, **kwargs)

    return wrapper


def ifPlayerVehicle(method):

    @wraps(method)
    def wrapper(mechanicComponent, *args, **kwargs):
        player = BigWorld.player()
        if mechanicComponent.isPlayerVehicle(player):
            method(mechanicComponent, player, *args, **kwargs)

    return wrapper


def ifObservedVehicle(method):

    @wraps(method)
    def wrapper(mechanicComponent, *args, **kwargs):
        player = BigWorld.player()
        vehicle = None if player is None else player.getVehicleAttached()
        if mechanicComponent.isObservedVehicle(player, vehicle):
            method(mechanicComponent, player, vehicle, *args, **kwargs)
        return

    return wrapper


def getVehicleMechanic(mechanicName, vehicle):
    return vehicle.dynamicComponents.get(mechanicName, None) if vehicle is not None else None


def getPlayerVehicleMechanic(mechanicName):
    vehicle = BigWorld.player().getVehicleAttached()
    return vehicle.dynamicComponents.get(mechanicName, None) if vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive() else None


def checkStateStatus(states=(), defReturn=None, abortAction=None):

    def decorator(method):

        @wraps(method)
        def wrapper(controller, *args, **kwargs):
            stateStatus = controller.stateStatus
            if stateStatus is not None and stateStatus.state in states:
                return method(controller, stateStatus, *args, **kwargs)
            else:
                return operator.methodcaller(abortAction)(controller) if abortAction is not None else defReturn

        return wrapper

    return decorator


def initOnce(method):

    @wraps(method)
    def wrapper(mechanicComponent, *args, **kwargs):
        if not hasattr(mechanicComponent, 'wasInited'):
            mechanicComponent.wasInited = True
            method(mechanicComponent, *args, **kwargs)

    return wrapper


class VehicleMechanicComponent(BigWorld.DynamicScriptComponent):

    def __init__(self):
        super(VehicleMechanicComponent, self).__init__()
        self.__componentDestroyed = False
        self.__appearanceInited = False

    def isAppearanceReady(self):
        return self.__appearanceInited and self.__isAppearanceReady()

    def isComponentDestroyed(self):
        return self.__componentDestroyed

    def isPlayerVehicle(self, player):
        return self.__isAvatarReady(player) and self.entity.id == player.playerVehicleID

    def isObservedVehicle(self, player, vehicle):
        return self.__isAvatarReady(player) and vehicle is not None and self.entity.id == vehicle.id

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


class VehicleMechanicPrefabComponent(VehicleMechanicComponent):
    _DEFAULT_OUTFIT = 'default'

    def __init__(self):
        super(VehicleMechanicPrefabComponent, self).__init__()
        self.__mechanicPrefab = ''
        self.__prefabRoot = None
        return

    def onDestroy(self):
        self.__mechanicPrefab = ''
        if self.__prefabRoot is not None:
            _logger.debug('[VehicleMechanic] removeGameObject (onDestroy) for %s', self.entity.id)
            CGF.removeGameObject(self.__prefabRoot)
            self.__prefabRoot = None
        super(VehicleMechanicPrefabComponent, self).onDestroy()
        return

    def _getMechanicPrefab(self, typeDescriptor, skin):
        raise NotImplementedError

    def _onAppearanceReady(self):
        appearance = self.entity.appearance
        skin = appearance.modelsSetParams.skin or self._DEFAULT_OUTFIT
        self.__mechanicPrefab = self._getMechanicPrefab(self.entity.typeDescriptor, skin)
        loadAppearancePrefab(self.__mechanicPrefab, appearance, self.__onMechanicPrefabLoaded)
        _logger.debug('[VehicleMechanic] loadAppearancePrefab for %s', self.entity.id)

    def __onMechanicPrefabLoaded(self, root):
        if not root.isValid:
            _logger.error('[VehicleMechanic] failed to load prefab: %s', self.__mechanicPrefab)
            return
        if self.isComponentDestroyed():
            _logger.debug('[VehicleMechanic] removeGameObject (onLoaded) for %s', self.entity.id)
            CGF.removeGameObject(root)
            return
        self.__prefabRoot = root


class VehicleMechanicGunPrefabComponent(VehicleMechanicPrefabComponent):
    _GUN_MAIN_PREFAB = 'main'

    def _getMechanicPrefab(self, typeDescriptor, skin):
        gunPrefabs = typeDescriptor.gun.prefabs
        skin = skin if skin in gunPrefabs else self._DEFAULT_OUTFIT
        return gunPrefabs[skin][self._GUN_MAIN_PREFAB][0]
