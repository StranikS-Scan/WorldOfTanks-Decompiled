# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/components/vehicle_component.py
import logging
import typing
import BigWorld
import CGF
from PlayerEvents import g_playerEvents
from vehicles.components.component_life_cycle import createComponentLifeCycleEvents, ILifeCycleComponent
from vehicles.components.component_wrappers import ifPlayerVehicle
from vehicle_systems.model_assembler import loadAppearancePrefab
if typing.TYPE_CHECKING:
    from Avatar import PlayerAvatar
    from items.vehicles import VehicleDescriptor
    from Vehicle import Vehicle
    from vehicles.components.component_life_cycle.life_cycle_interfaces import IComponentLifeCycleEvents
_logger = logging.getLogger(__name__)

class VehicleDynamicComponent(BigWorld.DynamicScriptComponent, ILifeCycleComponent):

    def __init__(self):
        super(VehicleDynamicComponent, self).__init__()
        self.__lifeCycleEvents = createComponentLifeCycleEvents(self)
        self.__componentDestroyed = False
        self.__appearanceInited = False

    @property
    def lifeCycleEvents(self):
        return self.__lifeCycleEvents

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
        self.__lifeCycleEvents.destroy()

    def onLeaveWorld(self):
        self.onDestroy()

    def onSiegeStateUpdated(self, typeDescriptor):
        if not self.__appearanceInited:
            return
        self._collectComponentParams(typeDescriptor)
        self.__lifeCycleEvents.processParamsCollected()
        self._updateComponentAvatar()

    def _initComponent(self):
        self.__initComponentAppearance()
        self.__initComponentAvatar()

    def _onAppearanceReady(self):
        self._collectComponentParams(self.entity.typeDescriptor)
        self.__lifeCycleEvents.processParamsCollected()

    def _onComponentAvatarUpdate(self, player):
        pass

    def _onComponentAppearanceUpdate(self):
        pass

    def _collectComponentParams(self, typeDescriptor):
        pass

    @ifPlayerVehicle
    def _onAvatarReady(self, player=None):
        pass

    @ifPlayerVehicle
    def _updateComponentAvatar(self, player=None):
        self._onComponentAvatarUpdate(player)

    def _updateComponentAppearance(self):
        if self.__appearanceInited and self.__isAppearanceReady():
            self._onComponentAppearanceUpdate()

    def __initComponentAvatar(self):
        if self.__isAvatarReady():
            self.__onAvatarReady()
        else:
            g_playerEvents.onAvatarReady += self.__onAvatarReady

    def __initComponentAppearance(self):
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
        self._onAvatarReady()
        self._updateComponentAvatar()

    def __onAppearanceReady(self):
        if self.__appearanceInited:
            return
        self._onAppearanceReady()
        self._onComponentAppearanceUpdate()
        self.__appearanceInited = True


class VehiclePrefabDynamicComponent(VehicleDynamicComponent):
    _DEFAULT_OUTFIT = 'default'

    def __init__(self):
        super(VehiclePrefabDynamicComponent, self).__init__()
        self.__componentPrefab = ''
        self._prefabRoot = None
        return

    def isPrefabRoot(self, gameObject):
        return self._prefabRoot is not None and self._prefabRoot.id == gameObject.id

    def onDestroy(self):
        self.__componentPrefab = ''
        if self._prefabRoot is not None:
            _logger.debug('[VehiclePrefabDynamicComponent] removeGameObject (onDestroy) for %s', self.entity.id)
            CGF.removeGameObject(self._prefabRoot)
            self._prefabRoot = None
        super(VehiclePrefabDynamicComponent, self).onDestroy()
        return

    def _getComponentPrefab(self, typeDescriptor, skin):
        raise NotImplementedError

    def _onAppearanceReady(self):
        super(VehiclePrefabDynamicComponent, self)._onAppearanceReady()
        loadAppearancePrefab(self.__componentPrefab, self.entity.appearance, self.__onComponentPrefabLoaded)
        _logger.debug('[VehiclePrefabDynamicComponent] loadAppearancePrefab for %s', self.entity.id)

    def _collectComponentParams(self, typeDescriptor):
        super(VehiclePrefabDynamicComponent, self)._collectComponentParams(typeDescriptor)
        skin = self.entity.appearance.modelsSetParams.skin or self._DEFAULT_OUTFIT
        self.__componentPrefab = self._getComponentPrefab(typeDescriptor, skin)

    def __onComponentPrefabLoaded(self, root):
        if not root.isValid:
            _logger.error('[VehiclePrefabDynamicComponent] failed to load prefab: %s', self.__componentPrefab)
            return
        if self.isComponentDestroyed():
            _logger.debug('[VehiclePrefabDynamicComponent] removeGameObject (onLoaded) for %s', self.entity.id)
            CGF.removeGameObject(root)
            return
        self._prefabRoot = root


class VehiclePrefabSetsDynamicComponent(VehiclePrefabDynamicComponent):
    _PREFABS_SET_KEY = ''

    def _getComponentPrefab(self, typeDescriptor, skin):
        prefabs = self._getComponentPrefabsSets(typeDescriptor)
        skin = skin if skin in prefabs else self._DEFAULT_OUTFIT
        return prefabs[skin][self._PREFABS_SET_KEY][0]

    def _getComponentPrefabsSets(self, typeDescriptor):
        raise NotImplementedError


class VehicleMechanicPrefabDynamicComponent(VehiclePrefabSetsDynamicComponent):
    _PREFABS_SET_KEY = 'mechanicEffects'

    def _getComponentPrefabsSets(self, typeDescriptor):
        return typeDescriptor.type.prefabs


class VehicleGunPrefabDynamicComponent(VehiclePrefabSetsDynamicComponent):
    _PREFABS_SET_KEY = 'main'

    def _getComponentPrefabsSets(self, typeDescriptor):
        return typeDescriptor.gun.prefabs
