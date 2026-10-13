# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWArenaInfoBossHealthBarComponent.py
from __future__ import absolute_import
import logging
import BigWorld
from collections import namedtuple
from helpers import dependency, isPlayerAvatar
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
_logger = logging.getLogger(__name__)
BossLive = namedtuple('Live', ['maxHP', 'minHP'])

def getArenaInfoBossHealthBarComponent():
    player = BigWorld.player()
    if not (player and isPlayerAvatar() and player.arena and player.arena.arenaInfo):
        return None
    else:
        arenaInfo = player.arena.arenaInfo
        return getattr(arenaInfo, 'HWArenaInfoBossHealthBarComponent', None)


class HWArenaInfoBossHealthBarComponent(DynamicScriptComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    __NO_LIVES_MIN_MAX_HEALTH = (0, 0)

    def __init__(self):
        super(HWArenaInfoBossHealthBarComponent, self).__init__()
        self.__isActive = False
        self.__lives = None
        self._livesHpRanges = []
        self._prevHealth = None
        return

    @property
    def isActive(self):
        return self.__isActive

    @property
    def prevHealth(self):
        return self._prevHealth or self.lastHealth

    @property
    def maxLives(self):
        return len(self.healthForLives)

    @property
    def livesLeft(self):
        return self.__getLifeNumByHealth()

    @property
    def hwBattleGuiCtrl(self):
        return self.guiSessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    @property
    def bossCount(self):
        return len(self.bossVehicleIDs)

    def clientOnBossHealthChanged(self, newHealth, prevHealth, bossVehicleID, attackerID, attackReasonID):
        if not self.__isActive:
            return
        self._prevHealth = prevHealth
        if self.__checkLivesChanged():
            self.__updateMarkerMaxHealth()
            if self.hwBattleGuiCtrl:
                self.hwBattleGuiCtrl.onBossLivesChanged()
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onBossHealthChanged(newHealth, prevHealth, bossVehicleID, attackerID, attackReasonID)
        if newHealth <= 0:
            self.__isActive = False

    def set_healthForLives(self, _):
        if self.__activate():
            if self.hwBattleGuiCtrl:
                self.hwBattleGuiCtrl.onBossHealthActivated()
        else:
            _logger.error('Cannot activate the component with data: %s, %d and %s', self.bossVehicleIDs, self.lastHealth, self.healthForLives)

    def set_minionsCount(self, prev):
        if self.__activate():
            if self.hwBattleGuiCtrl:
                self.hwBattleGuiCtrl.onBossMinionsCountChanged(self.minionsCount)

    def set_isVisible(self, prev):
        if self.__activate():
            if self.hwBattleGuiCtrl:
                self.hwBattleGuiCtrl.onBossHPBarVisibilityChanged(self.isVisible)

    def getBossCurrentLifeHealthValues(self):
        health = self.lastHealth
        if not self.isActive:
            return (health, health)
        lifeNum = self.__getLifeNumByHealth()
        lifeMinHealth, _ = self.__getMinMaxHealth(lifeNum)
        currentLifeHealth = health - lifeMinHealth
        return (currentLifeHealth, self.healthForLives[-lifeNum])

    def _onAvatarReady(self):
        if self.__activate():
            if self.hwBattleGuiCtrl:
                self.hwBattleGuiCtrl.onBossHealthActivated()
                self.hwBattleGuiCtrl.onBossMinionsCountChanged(self.minionsCount)
                self.hwBattleGuiCtrl.onBossHPBarVisibilityChanged(self.isVisible)

    def __setHealthRanges(self):
        if self._livesHpRanges:
            return
        maxHP = sum(self.healthForLives)
        for health in self.healthForLives:
            minHP = maxHP - health
            self._livesHpRanges.append(BossLive(maxHP, minHP))
            maxHP = minHP

    def __getMinMaxHealth(self, lifeNum):
        live = self._livesHpRanges[-lifeNum]
        return (live.minHP, live.maxHP)

    def __activate(self):
        if not (self.bossVehicleIDs and self.healthForLives and self.lastHealth > 0):
            return False
        self.__setHealthRanges()
        self.__isActive = True
        self.__lives = self.livesLeft
        self.__updateMarkerMaxHealth()
        return True

    def __checkLivesChanged(self):
        if self.livesLeft != self.__lives:
            self.__lives = self.livesLeft
            return True
        return False

    def __getLifeNumByHealth(self):
        health = self.lastHealth
        if health <= 0:
            return 0
        for lifeNum, live in enumerate(reversed(self._livesHpRanges), 1):
            if live.minHP <= health <= live.maxHP:
                return lifeNum

        return self.maxLives

    def __updateMarkerMaxHealth(self):
        livesLeft = self.livesLeft
        _, maxHealth = self.__getMinMaxHealth(livesLeft) if livesLeft > 0 else self.__NO_LIVES_MIN_MAX_HEALTH
        if self.hwBattleGuiCtrl:
            for bossVehicleID in self.bossVehicleIDs:
                self.hwBattleGuiCtrl.setVehicleMaxHealth(bossVehicleID, maxHealth)
