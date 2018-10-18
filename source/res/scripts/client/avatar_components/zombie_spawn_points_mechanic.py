# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/zombie_spawn_points_mechanic.py
from functools import partial
import logging
import BigWorld
import Math
import ArenaType
from helpers import newFakeModel
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from vehicle_systems import model_assembler
from vehicle_systems.tankStructure import ModelsSetParams, ModelStates
from items.vehicles import VehicleDescr, parseIntCompactDescr
from vehicle_systems.stricted_loading import _MAX_PRIORITY
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
_logger = logging.getLogger(__name__)

class ZombieSpawnPointsMechanic(object):
    zombieSpawnPoints = property(lambda self: self.__obstacles)

    def __init__(self):
        self.__enabled = False
        _logger.debug('[ZOMBIE_MECHANICS] ZombieSpawnPointsMechanic __init__')
        self.__zombieModels = {}
        self.__obstacles = None
        return

    def handleKey(self, isDown, key, mods):
        pass

    def onBecomePlayer(self):
        self.__enabled = BONUS_CAPS.checkAny(self.arenaBonusType, BONUS_CAPS.EVENT_BATTLES)
        _logger.debug('[ZOMBIE_MECHANICS] ZombieSpawnPointsMechanic onBecomePlayer. Enabled=%s', self.__enabled)

    def onBecomeNonPlayer(self):
        _logger.debug('[ZOMBIE_MECHANICS] ZombieSpawnPointsMechanic onBecomeNonPlayer. Enabled=%s', self.__enabled)
        self.__destroy()

    def createArenaObstacle(self, obstacles):
        self.__obstacles = obstacles
        if self.__enabled:
            _logger.debug('[ZOMBIE_MECHANICS] ZombieSpawnPointsMechanic createArenaObstacle. Obstacles=%s', obstacles)
            for guid, data in obstacles.iteritems():
                if guid not in self.__zombieModels:
                    vehTypeCompDescr = data['vehTypeCompDescr']
                    self.__zombieModels[guid] = _ZombieClientModel(data['position'], data['yaw'], data['pitch'], data['roll'], vehTypeCompDescr, self.spaceID)

    def destroyArenaObstacle(self, guid):
        if self.__enabled:
            _logger.debug('[ZOMBIE_MECHANICS] ZombieSpawnPointsMechanic destroyArenaObstacle. guid=%s', guid)
            if guid in self.__zombieModels:
                self.__zombieModels[guid].destroy(partial(self._onModelDestroyedCallback, guid))
            else:
                _logger.warn('[ZOMBIE_MECHANICS] Unable to delete obstacle. No obstacle object registered. %s', guid)

    def _onModelDestroyedCallback(self, guid):
        del self.__zombieModels[guid]

    def __destroy(self):
        _logger.debug('[ZOMBIE_MECHANICS] ZombieSpawnPointsMechanic:__destroy.')
        for model in self.__zombieModels.itervalues():
            model.destroy()

        self.__zombieModels.clear()


class _ZombieClientModel(object):
    _EFFECTS_LIST = {'uk:GB01_Medium_Mark_I_Halloween': 'ZombieWakeupSmallEffect',
     'ussr:R06_T-28_Halloween': 'ZombieWakeupMediumEffect',
     'france:F05_BDR_G1B_Halloween': 'ZombieWakeupLargeEffect'}

    def __init__(self, position, yaw, pitch, roll, vehTypeCompDescr, spaceID):
        _logger.debug('[ZOMBIE_MECHANICS] _ZombieClientModel. ModelName=%s, Position=%s', vehTypeCompDescr, position)
        self.__model = None
        self.__modelName = None
        self.__position = position
        self.__yaw = yaw
        self.__pitch = pitch
        self.__roll = roll
        self.__createModel(vehTypeCompDescr, spaceID)
        self.__effectPlayer = _ZombieEffectPlayer(position)
        return

    def destroy(self, callback=None):
        _logger.debug('[ZOMBIE_MECHANICS] destroy. Model name=%s', self.__modelName)
        if self.__model and self.__model in BigWorld.models():
            BigWorld.delModel(self.__model)
            self.__model = None
            if callback:
                destructionEffectName = self._EFFECTS_LIST.get(self.__modelName, 'ZombieWakeupSmallEffect')
                self.__effectPlayer.zombieSpawnEffect(destructionEffectName, callback)
            else:
                self.__effectPlayer.cleanup()
        else:
            _logger.warn('Unable to delete obstacle. No model created.')
        return

    def __createModel(self, vehTypeCompDescr, spaceID):
        descr = VehicleDescr(typeID=parseIntCompactDescr(vehTypeCompDescr)[1:])
        self.__modelName = descr.name
        modelsSetParams = ModelsSetParams(None, ModelStates.DESTROYED)
        assembler = model_assembler.prepareCompoundAssembler(descr, modelsSetParams, spaceID, False)
        BigWorld.loadResourceListBG((assembler,), self.__onModelLoaded, _MAX_PRIORITY)
        return

    def __onModelLoaded(self, resourceRefs):
        _logger.debug('[ZOMBIE_MECHANICS] __onModelLoaded. ModelName=%s', self.__modelName)
        if self.__modelName not in resourceRefs.failedIDs:
            self.__model = resourceRefs[self.__modelName]
            matrix = Math.Matrix()
            matrix.setRotateYPR((self.__yaw, self.__pitch, self.__roll))
            matrix.translation = self.__position
            self.__model.matrix = matrix
            BigWorld.addModel(self.__model)
        else:
            _logger.error('Model not found: %s', self.__modelName)


class _ZombieEffectPlayer(object):

    def __init__(self, position):
        self._effectsPlayer = None
        self._model = {}
        self._position = position
        return

    def zombieSpawnEffect(self, destructionEffectName, callback=None):
        effectsSection = ArenaType.g_cache[BigWorld.player().arenaTypeID].eventPointsPickupSettings.epEffects
        effect = effectsFromSection(effectsSection[destructionEffectName])
        self._model = newFakeModel()
        self._model.position = self._position
        BigWorld.addModel(self._model)
        self._effectsPlayer = EffectsListPlayer(effect.effectsList, effect.keyPoints)
        self._effectsPlayer.play(self._model, None, partial(self.cleanup, callback))
        return

    def cleanup(self, callback=None):
        if self._model and self._model in BigWorld.models():
            BigWorld.delModel(self._model)
            self._model = None
        if self._effectsPlayer:
            self._effectsPlayer.stop()
            self._effectsPlayer = None
        if callback:
            callback()
        return
