# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/drone_music_player.py
import BigWorld
from helpers import dependency
from gui.Scaleform.daapi.view.battle.shared.drone_music_player import DroneMusicPlayer, _Condition, _TimeRemainedCondition, _Severity, _initCondition
from skeletons.gui.battle_session import IBattleSessionProvider

class _HunterLifeCounter(_Condition):

    def __init__(self, criticalValue):
        super(_HunterLifeCounter, self).__init__(criticalValue, _Severity.MEDIUM)
        self._initialized = True

    @_initCondition
    def updateTeamHealth(self, *_):
        teamLivesComponent = BigWorld.player().arena.arenaInfo.dynamicComponents.get('teamLivesComponent')
        if teamLivesComponent:
            summa = sum(teamLivesComponent.teamLives.values())
            if summa <= self.criticalValue:
                return self._updateValidValue(True)
        return False


class _BossGeneratorCount(_Condition):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, criticalValue):
        super(_BossGeneratorCount, self).__init__(criticalValue, _Severity.MEDIUM)
        self._initialized = True
        self.__shieldIsDestroyed = False
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onPublicCounter += self.__onPublicCounter

    @_initCondition
    def updateTeamHealth(self, *_):
        return self._updateValidValue(True) if self.__shieldIsDestroyed else False

    def dispose(self):
        super(_BossGeneratorCount, self).dispose()
        feedback = self.__sessionProvider.shared.feedback
        if feedback:
            feedback.onPublicCounter -= self.__onPublicCounter

    def __onPublicCounter(self, name, count, maxCount):
        if count < self.criticalValue:
            self.__shieldIsDestroyed = True


class EventDroneMusicPlayer(DroneMusicPlayer):
    _SETTING_TO_CONDITION_MAPPING = {'timeRemained': (lambda player: True, (_TimeRemainedCondition,), lambda name, key, data: data[name][key]),
     'numberHunterLives': (lambda player: True, (_HunterLifeCounter,), lambda name, key, data: data[name][key]),
     'bossGeneratorCount': (lambda player: True, (_BossGeneratorCount,), lambda name, key, data: data[name][key])}
