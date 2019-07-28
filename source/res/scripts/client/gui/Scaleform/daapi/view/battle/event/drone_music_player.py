# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/drone_music_player.py
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from gui.Scaleform.daapi.view.battle.shared.drone_music_player import DroneMusicPlayer, _Condition, _TimeRemainedCondition, _Severity, _delegate, _initCondition
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class _EventCondition(_Condition):

    def onPlayerRespawnLivesUpdated(self, playerLivesLeft):
        return False

    def onCheckpointReached(self, maxCheckpoint, currentCheckpoint):
        return False


class _EventTimeRemainedCondition(_TimeRemainedCondition, _EventCondition):

    def __init__(self, criticalValue):
        super(_EventTimeRemainedCondition, self).__init__(criticalValue, _Severity.LOW)


class _WavesLeftCondition(_EventCondition):

    def __init__(self, criticalValue):
        super(_WavesLeftCondition, self).__init__(criticalValue, _Severity.LOW)

    def _isCriticalAchieved(self, wavesLeft):
        return self._updateValidValue(True) if wavesLeft <= self.criticalValue else False

    @_initCondition
    def onCheckpointReached(self, maxCheckpoint, currentCheckpoint):
        return self._isCriticalAchieved(maxCheckpoint - currentCheckpoint)


class _PlayerLivesRemainedCondition(_EventCondition):
    battleSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, criticalValue):
        super(_PlayerLivesRemainedCondition, self).__init__(criticalValue, _Severity.MEDIUM)

    def _isCriticalAchieved(self, livesLeft):
        return self._updateValidValue(True) if livesLeft <= self.criticalValue else False

    @_initCondition
    def onPlayerRespawnLivesUpdated(self, playerLivesLeft):
        return self._isCriticalAchieved(playerLivesLeft)


class EventDroneMusicPlayer(DroneMusicPlayer, GameEventGetterMixin):
    _SETTING_TO_CONDITION_MAPPING = {'timeRemained': (lambda player: True, (_EventTimeRemainedCondition,), lambda name, key, data: data[name][key]),
     'playerLivesRemained': (lambda player: True, (_PlayerLivesRemainedCondition,), lambda name, key, data: data[name][key]),
     'wavesRemained': (lambda player: True, (_WavesLeftCondition,), lambda name, key, data: data[name][key])}

    def __init__(self):
        super(EventDroneMusicPlayer, self).__init__()
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onPlayerRespawnLivesUpdated += self.onPlayerRespawnLivesUpdated
        checkpoints = self.checkpoints
        if checkpoints:
            checkpoints.onUpdated += self.__onCheckpointsUpdate
        return

    def detachedFromCtrl(self, ctrlID):
        super(EventDroneMusicPlayer, self).detachedFromCtrl(ctrlID)
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onPlayerRespawnLivesUpdated -= self.onPlayerRespawnLivesUpdated
        checkpoints = self.checkpoints
        if checkpoints:
            checkpoints.onUpdated -= self.__onCheckpointsUpdate
        return

    def __onCheckpointsUpdate(self):
        checkpoints = self.checkpoints
        if checkpoints:
            self.onCheckpointReached(checkpoints.getGoalValue(), checkpoints.getCurrentProgress())

    @_delegate
    def onCheckpointReached(self, maxCheckpoint, currentCheckpoint):
        pass

    @_delegate
    def onPlayerRespawnLivesUpdated(self, playerLivesLeft):
        pass
