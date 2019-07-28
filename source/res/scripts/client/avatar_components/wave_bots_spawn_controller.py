# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/wave_bots_spawn_controller.py
import logging
import cPickle
import BigWorld
import ResMgr
from constants import ARENA_BONUS_TYPE
from helpers import newFakeModel
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
_logger = logging.getLogger(__name__)
ENVIRONMENT_EFFECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'

class WaveBotsSpawnController(object):

    def __init__(self):
        self.__enabled = False
        self.__handlers = []

    def handleKey(self, isDown, key, mods):
        pass

    def onBecomePlayer(self):
        self.__enabled = self.arenaBonusType == ARENA_BONUS_TYPE.EVENT_BATTLES

    def onBecomeNonPlayer(self):
        if not self.__enabled:
            return
        for handler in self.__handlers:
            handler.stop()

    def notifyClients(self, notificationDataPickled):
        if not self.__enabled:
            return
        else:
            notificationData = cPickle.loads(notificationDataPickled)
            _logger.debug('[WAVE_BOT_SPAWN] WaveBotsSpawnController onWaveStarted. WaveName=%s', notificationData)
            handlerClass = NOTIFICATIONS_HANDLERS.get(notificationData['type'], None)
            handler = None
            if handlerClass is not None:
                handler = handlerClass(self, self.__cleanupCallback)
                handler.start(notificationData['params'])
                self.__handlers.append(handler)
            return

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

    def start(self, params):
        _logger.debug('[WAVE_BOT_SPAWN] _ClientEffectHandler start. Params = %s', params)
        position = params['position']
        effectName = None
        effectId = params.get('name', None)
        if effectId is not None:
            effectName = self._SPAWN_EFFECTS.get(effectId)
        else:
            _logger.error('No effect ID specified')
            self._cleanup()
            return
        self._model.position = (position[0], position[1], position[2])
        BigWorld.player().addModel(self._model)
        effectsSection = ResMgr.openSection(ENVIRONMENT_EFFECTS_CONFIG_FILE)
        effect = effectsFromSection(effectsSection[effectName])
        self._effectsPlayer = EffectsListPlayer(effect.effectsList, effect.keyPoints)
        self._effectsPlayer.play(self._model, None, self._cleanup)
        return

    def stop(self):
        if self._effectsPlayer:
            self._effectsPlayer.stop()
            self._effectsPlayer = None
        if self._model and self._model.inWorld is True:
            BigWorld.player().delModel(self._model)
            self._model = None
        return


class _ClientNotificationHandler(_BaseHandler):

    def start(self, params):
        _logger.debug('[WAVE_BOT_SPAWN] _ClientNotificationHandler start. Params = %s', params)
        battleHints = self._owner.guiSessionProvider.dynamic.battleHints
        if battleHints:
            data = {'waveSpawnedMessageData': params['waveName']}
            battleHints.showHint(params['hintName'], data)
        self._cleanup()


NOTIFICATIONS_HANDLERS = {'effect': _ClientEffectHandler,
 'hudNotify': _ClientNotificationHandler}
