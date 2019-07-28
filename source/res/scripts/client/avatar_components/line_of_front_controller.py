# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/line_of_front_controller.py
import logging
import cPickle
from collections import namedtuple
import BigWorld
import Event
import ResMgr
from constants import ARENA_BONUS_TYPE
from helpers import newFakeModel, isPlayerAvatar
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
from shared_utils import findFirst
_logger = logging.getLogger(__name__)
_EFFECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'
_LoFHealthNotificationRule = namedtuple('_LoFHealthNotificationRule', 'shouldBePlayed,soundNotificationId')

class LineOfFrontController(object):
    _MAX_HEALTH = 'maxHealth'
    _HEALTH = 'health'
    _VEH_ID = 'vehId'
    _DISAPPEAR_EFFECT_NAME = 'VehicleBotDisappearEffect'
    _PENETRATION_EFFECT_LAST = 'hb1_line_of_front_penetration_effect_last'
    _PENETRATION_NOTIFICATIONS_RULES = [_LoFHealthNotificationRule(lambda health, maxHealth: maxHealth - health == 1, 'hb1_line_of_front_penetration_effect_first'), _LoFHealthNotificationRule(lambda health, maxHealth: maxHealth / 2 == health, 'hb1_line_of_front_penetration_effect_half'), _LoFHealthNotificationRule(lambda health, maxHealth: health > 0, 'hb1_line_of_front_penetration_effect')]

    def __init__(self):
        self.__enabled = False
        self.__health = 0
        self.__maxHealth = 0
        self.__prevNotifiedHealth = None
        self.onHealthChanged = Event.Event()
        self.onMaxHealthChanged = Event.Event()
        self.onDamageByVehTypeChanged = Event.Event()
        self.onPotentialDamageChanged = Event.Event()
        self.onVehicleEnteredDangerZone = Event.Event()
        self.__effects = []
        self.__damageByVehType = {}
        self.__potentialDamage = 0
        return

    @property
    def lineOfFrontHealth(self):
        return self.__health

    @property
    def lineOfFrontHmaxHealth(self):
        return self.__maxHealth

    @property
    def potentialDamage(self):
        return self.__potentialDamage

    @property
    def damageByVehType(self):
        return self.__damageByVehType

    def handleKey(self, isDown, key, mods):
        pass

    def onBecomePlayer(self):
        self.__enabled = self.arenaBonusType == ARENA_BONUS_TYPE.EVENT_BATTLES

    def onBecomeNonPlayer(self):
        pass

    def onHealthDataChanged(self, dataPickled, potentialDamage):
        if not self.__enabled:
            return
        data = cPickle.loads(dataPickled)
        self.__maxHealth = self.__notify(self._MAX_HEALTH, self.__maxHealth, data.get(self._MAX_HEALTH), self.onMaxHealthChanged)
        self.__health = self.__notify(self._HEALTH, self.__health, data.get(self._HEALTH), self.onHealthChanged)
        self.__potentialDamage = potentialDamage
        self.__updatePotentialDamageIndicator()

    def onLineOfFrontPenetrated(self):
        if self.__health:
            self.__playPenetrationEffect(self.__health, self.__maxHealth)

    def vehicleEnteredLoFEffect(self, position):
        effectPlayer = _LineOfFrontEffectPlayer(position)
        effectPlayer.play(self._DISAPPEAR_EFFECT_NAME, self.__onEffectFinished)
        self.__effects.append(effectPlayer)

    def setConfigForCurrentMap(self, configPickled):
        if not self.__enabled:
            return
        self.__damageByVehType = cPickle.loads(configPickled)['damageByVehType']
        self.onDamageByVehTypeChanged()

    def onVehicleDangerousZoneTriggered(self, vehID, action, potentialDamage, position):
        if action == 'enter':
            self.__onVehicleEnteredDangerZone(position)
        self.__potentialDamage = potentialDamage
        self.__updatePotentialDamageIndicator()
        if self.__health - self.__potentialDamage <= 0 and self.__potentialDamage:
            self.soundNotifications.play(self._PENETRATION_EFFECT_LAST)

    def __updatePotentialDamageIndicator(self):
        self.onPotentialDamageChanged(self.__potentialDamage)

    def __onEffectFinished(self, effectObject):
        if isPlayerAvatar() and self.__effects and effectObject in self.__effects:
            self.__effects.remove(effectObject)
        else:
            _logger.debug('[LINE_OF_FRONT] No effect player registered: %s', effectObject)

    def __notify(self, name, currentValue, newValue, notification):
        if currentValue != newValue:
            notification(newValue)
        return newValue

    def __playPenetrationEffect(self, health, maxHealth):
        healthRange = (health, self.__prevNotifiedHealth)
        if self.__prevNotifiedHealth is None:
            healthRange = (health, health + 1)
        for _health in xrange(*healthRange):
            rule = findFirst(lambda rule: rule.shouldBePlayed(_health, maxHealth), self._PENETRATION_NOTIFICATIONS_RULES)
            self.soundNotifications.play(rule.soundNotificationId)

        self.__prevNotifiedHealth = health
        return

    def __onVehicleEnteredDangerZone(self, position):
        self.onVehicleEnteredDangerZone(position)


class _LineOfFrontEffectPlayer(object):

    def __init__(self, position):
        super(_LineOfFrontEffectPlayer, self).__init__()
        self.__model = newFakeModel()
        self.__effectsPlayer = None
        self.__position = position
        self.__callback = None
        return

    def play(self, effectName, callback):
        self.__callback = callback
        self.__model.position = self.__position
        BigWorld.player().addModel(self.__model)
        effectsSection = ResMgr.openSection(_EFFECTS_CONFIG_FILE)
        effect = effectsFromSection(effectsSection[effectName])
        self.__effectsPlayer = EffectsListPlayer(effect.effectsList, effect.keyPoints)
        self.__effectsPlayer.play(self.__model, None, self.__cleanup)
        return

    def __cleanup(self):
        if self.__callback:
            self.__callback(self)
        if self.__effectsPlayer:
            self.__effectsPlayer.stop()
            self.__effectsPlayer = None
        if self.__model and self.__model.inWorld is True:
            BigWorld.player().delModel(self.__model)
            self.__model = None
        return
