# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EventPointsPickup.py
from collections import namedtuple
import logging
import BigWorld
import Math
import ArenaType
from helpers import newFakeModel
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
from helpers.CallbackDelayer import CallbackDelayer
from constants import HALLOWEEN_EVEN_POINTS_MODEL_TYPE
from gui.battle_control import avatar_getter
_logger = logging.getLogger(__name__)
_EffectListPlayerDescr = namedtuple('EffectListPlayerDescr', ('effectListPlayer', 'effectEnd'))

class EventPointsPickup(BigWorld.Entity):
    _MUTATOR_VERTICAL_OFFSET = 2.0
    _MUTATOR_PICKUP_EFFECT_NAME = 'MutatorChestPickupEffect'
    _MUTATOR_PICKUP_SILENT_EFFECT_NAME = 'MutatorChestPickupEffect'
    _MUTATOR_IDLE_EFFECT_NAME = 'MutatorChestIdleEffect'
    _DEATH_VERTICAL_OFFSET = 0.8
    _FREE_SOULS_COUNT = 1
    _STATIC_IDLE_VISUAL_MODEL_NAME = 'particles/content_deferred/GFX_models/environment/Halloween2018_Ghost_Cone.model'
    _STATIC_IDLE_VISUAL_MODEL_DELAY = 2.0
    _STATIC_IDLE_VISUAL_MODEL_SCALE = (8.0, 14.0, 8.0)
    _STATIC_IDLE_VISUAL_MODEL_VERT_OFFSET = -11.0

    def __init__(self):
        super(EventPointsPickup, self).__init__(self)
        self._callbackDelayer = CallbackDelayer()
        self._fakeModel = None
        self._model = None
        self._effects = {}
        self._effectsPlayer = None
        self._zombieDeathEffectName = None
        self._soulsPickupEffectName = None
        self._soulsPickupSilentEffectName = None
        self._idleEffectName = None
        self._zombieDeathEffectOffset = None
        self._soulsPickupEffectOffset = None
        self._idleEffectOffset = None
        self._modelName = None
        self._startDelay = None
        self._modelScale = None
        self._verticalOffset = None
        return

    def prerequisites(self):
        prereqs = []
        self._pickupSettings = ArenaType.g_cache[BigWorld.player().arenaTypeID].eventPointsPickupSettings
        if self.modelType == HALLOWEEN_EVEN_POINTS_MODEL_TYPE.CROSS:
            self._chooseEffectsBySoulsCount()
        elif self.modelType == HALLOWEEN_EVEN_POINTS_MODEL_TYPE.CHEST:
            self._chooseChestEffects()
        else:
            _logger.error('Incorrect Pickup model type: %s', self.modelType)
        self._createEffectObjects(prereqs)
        return prereqs

    def onEnterWorld(self, prereqs):
        if not self.eventPoints:
            return
        else:
            self._fakeModel = self._prepareModel()
            delay = 0.0
            if self.eventPoints > self._FREE_SOULS_COUNT and self._zombieDeathEffectName is not None:
                delay = self._playZombieDeathEffect()
            self._callbackDelayer.delayCallback(delay, self._playIdleEffect)
            return

    def onLeaveWorld(self):
        self._cleanup()

    def set_isRemoving(self, prev):
        isOwnVeh = avatar_getter.getPlayerVehicleID() == self.vehicleID
        self._playSoulsPickupEffect(isOwnVehicle=isOwnVeh)

    def _playZombieDeathEffect(self):
        delay, _ = self._playEffect(self._zombieDeathEffectName, self._zombieDeathEffectOffset)
        return delay

    def _playIdleEffect(self):
        _, effectListPlayer = self._playEffect(self._idleEffectName, self._idleEffectOffset)
        self._effectsPlayer = effectListPlayer
        self._callbackDelayer.delayCallback(self._startDelay, self._showStaticIdleEffect)

    def _showStaticIdleEffect(self):
        if self._model is None:
            self._model = BigWorld.Model(self._modelName)
            self._model.position = self.position + Math.Vector3(0.0, self._verticalOffset, 0.0)
            self._model.scale = self._modelScale
            BigWorld.player().addModel(self._model)
        return

    def _delStaticIdleEffect(self):
        if self._model is not None:
            BigWorld.player().delModel(self._model)
            self._model = None
        return

    def _playSoulsPickupEffect(self, isOwnVehicle=True):
        effectName = self._soulsPickupEffectName
        if not isOwnVehicle:
            effectName = self._soulsPickupSilentEffectName
        delay, _ = self._playEffect(effectName, self._soulsPickupEffectOffset)
        self._callbackDelayer.delayCallback(delay, self._cleanup)

    def _playEffect(self, effectName, effectVerticalOffset):
        effectPlayerDesr = self._effects.get(effectName)
        self._fakeModel.position = self.position + Math.Vector3(0.0, effectVerticalOffset, 0.0)
        effectPlayerDesr.effectListPlayer.play(self._fakeModel)
        return (effectPlayerDesr.effectEnd, effectPlayerDesr.effectListPlayer)

    def _chooseEffectsBySoulsCount(self):
        halloweenEffectsSettings = ArenaType.g_cache[BigWorld.player().arenaTypeID].halloweenEffectsSettings
        for rewardAmount in sorted(halloweenEffectsSettings, reverse=True):
            if self.eventPoints >= rewardAmount > 0:
                rewardEffects = halloweenEffectsSettings[rewardAmount]
                self._zombieDeathEffectName = rewardEffects['zombieDeathEffect']['name']
                self._zombieDeathEffectOffset = rewardEffects['zombieDeathEffect']['verticalOffset']
                self._soulsPickupEffectOffset = rewardEffects['soulsPickupEffect']['verticalOffset']
                self._idleEffectName = rewardEffects['idleEffect']['name']
                self._idleEffectOffset = rewardEffects['idleEffect']['verticalOffset']
                self._soulsPickupEffectName = rewardEffects['soulsPickupEffect']['name']
                self._soulsPickupSilentEffectName = rewardEffects['soulsPickupEffect']['nameSilent']
                self._modelName = rewardEffects['idleStaticEffect']['modelName']
                self._startDelay = rewardEffects['idleStaticEffect']['startDelay']
                self._modelScale = rewardEffects['idleStaticEffect']['modelScale']
                self._verticalOffset = rewardEffects['idleStaticEffect']['verticalOffset']
                break

    def _chooseChestEffects(self):
        self._soulsPickupEffectName = EventPointsPickup._MUTATOR_PICKUP_EFFECT_NAME
        self._soulsPickupSilentEffectName = EventPointsPickup._MUTATOR_PICKUP_SILENT_EFFECT_NAME
        self._soulsPickupEffectOffset = EventPointsPickup._MUTATOR_VERTICAL_OFFSET
        self._idleEffectName = EventPointsPickup._MUTATOR_IDLE_EFFECT_NAME
        self._idleEffectOffset = EventPointsPickup._MUTATOR_VERTICAL_OFFSET
        self._modelName = EventPointsPickup._STATIC_IDLE_VISUAL_MODEL_NAME
        self._startDelay = EventPointsPickup._STATIC_IDLE_VISUAL_MODEL_DELAY
        self._modelScale = EventPointsPickup._STATIC_IDLE_VISUAL_MODEL_SCALE
        self._verticalOffset = EventPointsPickup._STATIC_IDLE_VISUAL_MODEL_VERT_OFFSET

    def _createEffectObjects(self, prereqs):
        self._addEffectToEffectsDict(self._zombieDeathEffectName, prereqs)
        self._addEffectToEffectsDict(self._soulsPickupEffectName, prereqs)
        self._addEffectToEffectsDict(self._soulsPickupSilentEffectName, prereqs)
        self._addEffectToEffectsDict(self._idleEffectName, prereqs)

    def _addEffectToEffectsDict(self, effectName, prereqs):
        if effectName is None:
            return
        else:
            effect = effectsFromSection(self._pickupSettings.epEffects[effectName])
            prereqs.extend(effect.effectsList.prerequisites())
            effectEnd = 0
            for keyPoint in effect.keyPoints:
                if keyPoint.name == 'effectEnd':
                    effectEnd = keyPoint.time

            self._effects[effectName] = _EffectListPlayerDescr(EffectsListPlayer(effect.effectsList, effect.keyPoints), effectEnd)
            return

    def _prepareModel(self):
        model = newFakeModel()
        model.position = self.position
        BigWorld.player().addModel(model)
        return model

    def _cleanup(self):
        self._callbackDelayer.destroy()
        self._callbackDelayer = None
        if self._effectsPlayer:
            self._effectsPlayer.stop()
            self._effectsPlayer = None
        if self._fakeModel and self._fakeModel.inWorld is True:
            BigWorld.player().delModel(self._fakeModel)
            self._fakeModel = None
        self._delStaticIdleEffect()
        self._effects.clear()
        return
