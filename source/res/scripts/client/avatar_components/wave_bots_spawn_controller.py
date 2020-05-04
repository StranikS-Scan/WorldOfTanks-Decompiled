# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/wave_bots_spawn_controller.py
import logging
import cPickle
import BigWorld
import Event
import ResMgr
from constants import ARENA_BONUS_TYPE
from gui.battle_control import avatar_getter
from helpers import newFakeModel
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
_logger = logging.getLogger(__name__)
ENVIRONMENT_EFFECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'

class WaveBotsSpawnController(object):

    def __init__(self):
        self.__enabled = False
        self.__handlers = []
        self.__botRoles = dict()
        self.__botMarkersType = dict()
        self.onBotRolesReceived = Event.Event()
        self.onBotBehaviorReceived = Event.Event()
        self.onBotBehaviorUpdate = Event.Event()
        self.onVehicleSpawnEffectStarted = Event.Event()
        self.onVehicleSpawnNotification = Event.Event()
        self.__waveToNotify = {'wave_1_2',
         'wave_2_2',
         'S1_stage1_wave2a',
         'S2_stage1_wave2a',
         'S2_stage2_wave_2a',
         'atc_2_1',
         'atc_3_1',
         'atc_5',
         'attack',
         'MT_3_1',
         'push_scene_2_3',
         'scene_b2_wave_5'}

    def handleKey(self, isDown, key, mods):
        pass

    def onBecomePlayer(self):
        self.__enabled = self.arenaBonusType == ARENA_BONUS_TYPE.EVENT_BATTLES
        self.onVehicleSpawnNotification += self.__counterattackNotification

    def onBecomeNonPlayer(self):
        self.onVehicleSpawnNotification -= self.__counterattackNotification
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

    def setBotRoles(self, botRoles):
        self.__botRoles.update(botRoles)

    def setBotMarkersType(self, botMarkersType):
        self.__botMarkersType.update(botMarkersType)

    def getBotRole(self, vehicleID):
        return self.__botRoles.get(vehicleID, '')

    def getBotMarkerType(self, vehicleID):
        return self.__botMarkersType.get(vehicleID, '')

    def getBotMarkerTypes(self):
        return self.__botMarkersType

    def setBotMarkerType(self, vehicleID, markerType):
        self.__botMarkersType.update({vehicleID: markerType})

    def __counterattackNotification(self, waveUID, **kwargs):
        if not kwargs.get('botsWaveUID', False) and waveUID in self.__waveToNotify:
            avatar_getter.getSoundNotifications().play('se20_enemy_counterattack')
            self.__waveToNotify.remove(waveUID)

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
    _SPAWN_EFFECT = 'VehicleBotPreSpawnEffect'

    def __init__(self, owner, cleanupCallback):
        super(_ClientEffectHandler, self).__init__(owner, cleanupCallback)
        self._model = newFakeModel()
        self._effectsPlayer = None
        return

    def start(self, params):
        _logger.debug('[WAVE_BOT_SPAWN] _ClientEffectHandler start. Params = %s', params)
        position = params['position']
        self._model.position = (position[0], position[1], position[2])
        BigWorld.player().addModel(self._model)
        self._owner.onVehicleSpawnEffectStarted(position, params['botRole'])
        if self._SPAWN_EFFECT:
            effectsSection = ResMgr.openSection(ENVIRONMENT_EFFECTS_CONFIG_FILE)
            effect = effectsFromSection(effectsSection[self._SPAWN_EFFECT])
            self._effectsPlayer = EffectsListPlayer(effect.effectsList, effect.keyPoints)
            self._effectsPlayer.play(self._model, None, self._cleanup)
        waveUID = params.get('waveUID', None)
        if params['notifyMinimap']:
            self.__minimapNotification(waveUID)
        return

    def stop(self):
        if self._effectsPlayer:
            self._effectsPlayer.stop()
            self._effectsPlayer = None
        if self._model and self._model.inWorld is True:
            BigWorld.player().delModel(self._model)
            self._model = None
        return

    def __minimapNotification(self, waveUID):
        self._owner.onVehicleSpawnNotification(waveUID)


class _ClientNotificationHandler(_BaseHandler):

    def start(self, params):
        _logger.debug('[WAVE_BOT_SPAWN] _ClientNotificationHandler start. Params = %s', params)
        battleHints = self._owner.guiSessionProvider.dynamic.battleHints
        if battleHints:
            data = {'waveSpawnedMessageData': params['waveName']}
            battleHints.showHint(params['hintName'], data)
        self._cleanup()


class _ClientBotDataHandler(_BaseHandler):

    def start(self, params):
        _logger.debug('[WAVE_BOT_SPAWN] _ClientBotDataHandler start. Params = %s', params)
        self._owner.setBotRoles(params.get('botRoles'))
        self._owner.setBotMarkersType(params.get('botMarkersType'))
        self._owner.onVehicleSpawnNotification(None, botsWaveUID=params.get('botsWaveUID'))
        self._owner.onBotRolesReceived()
        self._owner.onBotBehaviorUpdate()
        return


NOTIFICATIONS_HANDLERS = {'effect': _ClientEffectHandler,
 'hudNotify': _ClientNotificationHandler,
 'botVehicleDataNotify': _ClientBotDataHandler}
