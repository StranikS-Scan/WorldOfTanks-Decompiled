# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/map_scenario_progress.py
import BigWorld
from gui.Scaleform.daapi.view.meta.MapScenarioProgressMeta import MapScenarioProgressMeta
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from gui.Scaleform.locale.EVENT import EVENT
from helpers import isPlayerAvatar

class MapScenarioProgress(MapScenarioProgressMeta, GameEventGetterMixin):

    def __init__(self):
        super(MapScenarioProgress, self).__init__()
        self.__maxHealth = 0
        self.__health = 0
        self.__potentialDamage = 0
        self.__firstHealth = True
        self.__firstDamage = True
        self.__waveMaxValueInited = False

    def _populate(self):
        super(MapScenarioProgress, self)._populate()
        checkpoints = self.checkpoints
        if checkpoints:
            checkpoints.onUpdated += self.__onCheckpointsUpdate
            self.__onCheckpointsUpdate()
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onHealthChanged += self.__onHealthChanged
            player.onMaxHealthChanged += self.__onMaxHealthChanged
            player.onPotentialDamageChanged += self.__onPotentialDamageChanged
            self.__onMaxHealthChanged(player.lineOfFrontHmaxHealth)
            self.__onHealthChanged(player.lineOfFrontHealth)
            self.__onPotentialDamageChanged(player.potentialDamage)
        self.as_setTitleBaseS(EVENT.MAP_SCENARIO_PROGRESS_BASE_TITLE)
        self.as_setTitleWaveS(EVENT.MAP_SCENARIO_PROGRESS_WAVE_TITLE)

    def _dispose(self):
        checkpoints = self.checkpoints
        if checkpoints:
            checkpoints.onUpdated -= self.__onCheckpointsUpdate
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onHealthChanged -= self.__onHealthChanged
            player.onMaxHealthChanged -= self.__onMaxHealthChanged
            player.onPotentialDamageChanged -= self.__onPotentialDamageChanged
        super(MapScenarioProgress, self)._dispose()

    def __onCheckpointsUpdate(self):
        checkpoints = self.checkpoints
        if checkpoints:
            goalValue = checkpoints.getGoalValue()
            if not self.__waveMaxValueInited and goalValue > 0:
                self.as_setMaxValueWaveS(goalValue)
                self.__waveMaxValueInited = True
            self.as_setCurrentValueWaveS(checkpoints.getCurrentProgress())

    def __onMaxHealthChanged(self, newValue):
        if newValue != self.__maxHealth:
            self.__maxHealth = newValue
            self.as_setMaxValueBaseS(newValue)

    def __onHealthChanged(self, health):
        if health != self.__health:
            self.__health = health
            self.__updateLoFIndicatorStatus(self.__firstHealth)
            if self.__firstHealth:
                self.__firstHealth = False

    def __onPotentialDamageChanged(self, potentialDamage):
        if potentialDamage != self.__potentialDamage:
            self.__potentialDamage = potentialDamage
            self.__updateLoFIndicatorStatus(self.__firstDamage)
            if self.__firstDamage:
                self.__firstDamage = False

    def __updateLoFIndicatorStatus(self, isNoAnim):
        self.as_setCurrentValueProbableDamageBaseS(self.__health, self.__potentialDamage, isNoAnim)
