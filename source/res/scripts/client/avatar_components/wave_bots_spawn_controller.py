# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/wave_bots_spawn_controller.py
import logging
import cPickle
import zlib
import BigWorld
import Event
from constants import ARENA_BONUS_TYPE, EVENT_BOT_ROLE
from helpers import newFakeModel
from effect_controller import EffectController
_logger = logging.getLogger(__name__)
ENVIRONMENT_EFFECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'

class WaveBotsSpawnController(object):

    def __init__(self):
        self.__enabled = False
        self.__handlers = []
        self.__botRoles = dict()
        self.onBotRolesReceived = Event.Event()
        self.onVehicleSpawnEffectStarted = Event.Event()
        self.onVehicleSpawnNotification = Event.Event()

    def handleKey(self, isDown, key, mods):
        pass

    def onBecomePlayer(self):
        self.__enabled = self.arenaBonusType == ARENA_BONUS_TYPE.EVENT_BATTLES

    def onBecomeNonPlayer(self):
        if not self.__enabled:
            return
        for handler in self.__handlers:
            handler.stop()

    def notifyClients(self, notificationDataPacked):
        if not self.__enabled:
            return
        else:
            notificationData = cPickle.loads(zlib.decompress(notificationDataPacked))
            _logger.debug('[WAVE_BOT_SPAWN] WaveBotsSpawnController onWaveStarted. WaveName=%s', notificationData)
            handlerClass = NOTIFICATIONS_HANDLERS.get(notificationData['type'], None)
            handler = None
            if handlerClass is not None:
                handler = handlerClass(self, self.__cleanupCallback)
                handler.start(notificationData['params'])
                self.__handlers.append(handler)
            return

    def setBotRoles(self, botRoles):
        self.__botRoles.update(botRoles)

    def removeBotRole(self, vehID):
        if vehID in self.__botRoles:
            self.__botRoles.pop(vehID)

    def getBotRole(self, vehicleID):
        return self.__botRoles.get(vehicleID, '')

    def isBoss(self, vehicleID):
        return self.getBotRole(vehicleID) == EVENT_BOT_ROLE.BOSS

    def __cleanupCallback(self, handler):
        if handler in self.__handlers:
            self.__handlers.remove(handler)
        else:
            _logger.warning('Handler object is not registered in handlers list. %s', handler)


class _BaseHandler(object):

    def __init__(self, owner, cleanupCallback):
        self._cleanupCallback = cleanupCallback
        self._owner = owner

    def start(self, callback):
        raise NotImplementedError

    def stop(self):
        pass

    def _cleanup(self):
        self.stop()
        self._cleanupCallback(self)


class _ClientEffectHandler(_BaseHandler):
    _SPAWN_EFFECTS = {'botSpawn': 'VehicleBotPreSpawnEffect'}

    def __init__(self, owner, cleanupCallback):
        super(_ClientEffectHandler, self).__init__(owner, cleanupCallback)
        self._model = newFakeModel()
        self._spawnEffect = None
        return

    def start(self, params):
        _logger.debug('[WAVE_BOT_SPAWN] _ClientEffectHandler start. Params = %s', params)
        position = params['position']
        self._model.position = (position[0], position[1], position[2])
        BigWorld.player().addModel(self._model)
        self._owner.onVehicleSpawnEffectStarted(position, params['botRole'])
        self._spawnEffect = EffectController('creep_spawn')
        self._spawnEffect.playSequence(self._model)
        if params['notifyMinimap']:
            self.__minimapNotification(position)

    def stop(self):
        if self._spawnEffect:
            self._spawnEffect.reset()
            self._spawnEffect = None
        if self._model and self._model.inWorld is True:
            BigWorld.player().delModel(self._model)
            self._model = None
        return

    def __minimapNotification(self, position):
        self._owner.onVehicleSpawnNotification(position)


class _ClientNotificationHandler(_BaseHandler):

    def start(self, params):
        _logger.debug('[WAVE_BOT_SPAWN] _ClientNotificationHandler start. Params = %s', params)
        battleHints = self._owner.guiSessionProvider.dynamic.battleHints
        if battleHints:
            data = {'waveSpawnedMessageData': params['waveName']}
            battleHints.showHint(params['hintName'], data)
        self._cleanup()


class _ClientBotRolesHandler(_BaseHandler):

    def start(self, params):
        _logger.debug('[WAVE_BOT_SPAWN] _ClientBotRolesHandler start. Params = %s', params)
        self._owner.setBotRoles(params.get('botRoles'))
        self._owner.onBotRolesReceived()


NOTIFICATIONS_HANDLERS = {'effect': _ClientEffectHandler,
 'hudNotify': _ClientNotificationHandler,
 'botVehicleRoleNotify': _ClientBotRolesHandler}
