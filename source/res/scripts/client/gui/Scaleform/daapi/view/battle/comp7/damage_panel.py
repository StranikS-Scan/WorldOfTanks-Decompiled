# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/damage_panel.py
import logging
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.damage_panel import DamagePanel, STATUS_ID, ConcurrentStatusManager
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
_logger = logging.getLogger(__name__)

class Comp7DamagePanel(DamagePanel):

    def _getConcurrentStatusManager(self):
        return _Comp7ConcurrentStatusManager

    def _updateStun(self, stunInfo):
        self.__updateCrewStun(buffName=VEHICLE_VIEW_STATE.STUN, isActive=stunInfo.endTime > 0, duration=stunInfo.endTime)

    def _updateCrewBuff(self, buffName, isActive, duration):
        self.__updateEffect(buffName, isActive, duration, self._statusAnimPlayers[STATUS_ID.BUFF])

    def __updateCrewStun(self, buffName, isActive, duration):
        self.__updateEffect(buffName, isActive, duration, self._statusAnimPlayers[STATUS_ID.STUN])

    def __updateEffect(self, buffName, isActive, duration, animationPlayer):
        if isActive:
            self._crewBuffManager.setStatus(buffName, duration, animationPlayer)
        else:
            self._crewBuffManager.deleteStatus(buffName)


_STATUS_EFFECTS_PRIORITY = (VEHICLE_VIEW_STATE.AOE_INSPIRE, VEHICLE_VIEW_STATE.AOE_HEAL, VEHICLE_VIEW_STATE.STUN)

class _Comp7ConcurrentStatusManager(ConcurrentStatusManager):

    def setStatus(self, statusName, endTime, animationPlayer=None):
        self._currentStatuses[statusName] = (endTime, animationPlayer or self._animationPlayer)
        self._updateBuffAnimation()

    def deleteStatus(self, statusName):
        self._currentStatuses.pop(statusName, None)
        self._updateBuffAnimation()
        return

    def _getEffectsPriority(self, effect):
        try:
            return _STATUS_EFFECTS_PRIORITY.index(effect)
        except ValueError:
            return -1

    def _updateBuffAnimation(self):
        self._exposedStatusEndTime, self._exposedStatus = (0, None)
        currTime = BigWorld.serverTime()
        sortedStatuses = sorted(self._currentStatuses.keys(), key=self._getEffectsPriority, reverse=False)
        if sortedStatuses:
            buffName = sortedStatuses[0]
            endTime, animationPlayer = self._currentStatuses[buffName]
            if animationPlayer != self._animationPlayer:
                self._animationPlayer.hideStatus(True)
                self._animationPlayer = animationPlayer
            if endTime > self._exposedStatusEndTime:
                self._exposedStatus = buffName
                self._exposedStatusEndTime = endTime
        timeLeft = self._exposedStatusEndTime - currTime
        if timeLeft > 0:
            self._animationPlayer.showStatus(timeLeft, not self._animationPlayer.hasStatus())
        else:
            self._animationPlayer.hideStatus(True)
        return None
