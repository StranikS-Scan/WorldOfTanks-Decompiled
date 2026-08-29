# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/comp7_equipment_component.py
from collections import defaultdict
import cPickle
import typing
import logging
import GenericComponents
import zlib
import BigWorld
import CGF
import Math
import math_utils
from arena_component_system.client_arena_component_system import ClientArenaComponent
from constants import ARENA_UPDATE
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import Comp7Keys
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from helpers import dependency
from items import vehicles
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IComp7Controller
_logger = logging.getLogger(__name__)

class Comp7EquipmentComponent(ClientArenaComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, componentSystem):
        super(Comp7EquipmentComponent, self).__init__(componentSystem)
        self.__effects = defaultdict(dict)
        self._onUpdate = {ARENA_UPDATE.VEHICLE_UPDATED: self.__onVehicleUpdated}

    def activate(self):
        super(Comp7EquipmentComponent, self).activate()
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        return

    def deactivate(self):
        ctrl = self.__sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        self.__clear()
        super(Comp7EquipmentComponent, self).deactivate()
        return

    def __clear(self):
        for effects in self.__effects.itervalues():
            for effect in effects.itervalues():
                effect.destroy()

            effects.clear()

        self.__effects.clear()

    def __onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_AOE_HEAL:
            self.__updateAoeEffect(eventID=eventID, vehicleID=vehicleID, value=value, effectClass=_AoeHealEffect)

    def __updateAoeEffect(self, eventID, vehicleID, value, effectClass):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is None:
            return
        else:
            effects = self.__effects[eventID]
            if effectClass.isVisible(vehicle, value):
                if vehicleID not in effects:
                    effects[vehicleID] = effect = effectClass(parent=vehicle.entityGameObject, vehicle=vehicle)
                    effect.start()
            else:
                effect = effects.pop(vehicleID, None)
                if effect is not None:
                    effect.destroy()
            return

    def __onVehicleUpdated(self, argStr):
        infoAsTuple = cPickle.loads(zlib.decompress(argStr))
        arena = avatar_getter.getArena()
        if arena and len(infoAsTuple) >= 30:
            stats = dict()
            stats[infoAsTuple[0]] = {Comp7Keys.ROLE_SKILL: infoAsTuple[29]}
            arena.onGameModeSpecificStats(isStatic=True, stats=stats)


class _Effect(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    _dynObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)

    def __init__(self, parent, vehicle):
        self._parent = parent
        self._vehicle = vehicle
        self._prefab = None
        self.__destroyed = False
        return

    @property
    def radius(self):
        if self._vehicle is None or not hasattr(self._vehicle, 'selectedComp7Skill'):
            _logger.error('Missing selectedComp7Skill component at vehicle: %s', self._vehicle.id)
            return
        else:
            equipmentID = self._vehicle.selectedComp7Skill
            equipment = vehicles.g_cache.equipments()[equipmentID]
            return equipment.radius

    def start(self):
        self._load()

    def destroy(self):
        if self._prefab is not None:
            if self._prefab.isValid():
                CGF.removeGameObject(self._prefab)
            self._prefab = None
        self.__destroyed = True
        return

    @staticmethod
    def isVisible(vehicle, value, checkTeam=True):
        if value.get('finishing', False):
            return False
        return False if checkTeam and vehicle.publicInfo['team'] != avatar_getter.getPlayerTeam() else value.get('isSourceVehicle', False)

    def _load(self):
        path = self._getPath()
        parent = self._getParent()
        position = self._getPosition()
        CGF.loadGameObjectIntoHierarchy(path, parent, position, self._onLoaded)

    def _onLoaded(self, prefab):
        if not self.__destroyed:
            self._prefab = prefab
            self._updateRadius()
            self._prefab.activate()
        else:
            CGF.removeGameObject(prefab)

    def _getPath(self):
        raise NotImplementedError

    def _getParent(self):
        return self._parent

    def _getPosition(self):
        return Math.Vector3()

    @classmethod
    def _getDynObjectsCacheConfig(cls):
        arenaGuiType = cls.__sessionProvider.arenaVisitor.getArenaGuiType()
        return cls._dynObjectsCache.getConfig(arenaGuiType)

    def _updateRadius(self):
        if self._prefab is None:
            _logger.error('Failed to update Effect radius. Missing prefab.')
            return
        else:
            terrainSelectedArea = self._prefab.findComponentByType(GenericComponents.TerrainSelectedAreaComponent)
            if terrainSelectedArea is None:
                _logger.error('Failed to update Effect radius. Missing TerrainSelectedArea component.')
                return
            terrainSelectedArea.size = Math.Vector2(self.radius * 2, self.radius * 2)
            return


class _AoeHealEffect(_Effect):

    def _getPath(self):
        return self._getDynObjectsCacheConfig().getAoeHealPrefab()

    def _updateRadius(self):
        super(_AoeHealEffect, self)._updateRadius()
        transformComponent = self._prefab.findComponentByType(GenericComponents.TransformComponent)
        if transformComponent is None:
            _logger.error('Failed to update Effect radius. Missing TransformComponent component.')
            return
        else:
            transformComponent.transform = math_utils.createSRTMatrix(Math.Vector3(self.radius, 1.0, self.radius), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
            return
