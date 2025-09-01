# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/drone_music_player.py
from helpers import dependency
from gui.Scaleform.daapi.view.battle.shared.drone_music_player import DroneMusicPlayer, _Condition, _TimeRemainedCondition, _Severity, _initCondition, _delegate
from skeletons.gui.battle_session import IBattleSessionProvider
from white_tiger.cgf_components import wt_helpers

class _WTCondition(_Condition):

    def onGeneratorDestroyed(self, generatorsLeft):
        return False


class _WTTimeRemainedCondition(_TimeRemainedCondition):

    def onGeneratorDestroyed(self, _):
        pass


class _WTBossGeneratorCountCondition(_WTCondition):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, criticalValue):
        super(_WTBossGeneratorCountCondition, self).__init__(criticalValue, _Severity.MEDIUM)
        self._initialized = True

    @_initCondition
    def onGeneratorDestroyed(self, generatorsLeft):
        return self._updateValidValue(True) if generatorsLeft < self.criticalValue else self._updateValidValue(False)


class WTDroneMusicPlayer(DroneMusicPlayer):
    _SETTING_TO_CONDITION_MAPPING = {'timeRemained': (lambda player: True, (_WTTimeRemainedCondition,), lambda name, key, data: data[name][key]),
     'wtBossGeneratorCount': (lambda player: True, (_WTBossGeneratorCountCondition,), lambda name, key, data: data[name][key])}

    def __init__(self):
        super(WTDroneMusicPlayer, self).__init__()
        battleStateComponent = wt_helpers.getBattleStateComponent()
        if battleStateComponent:
            battleStateComponent.onGeneratorsLeftInitialize += self.onGeneratorDestroyed
            battleStateComponent.onGeneratorDestroyed += self.onGeneratorDestroyed

    @_delegate
    def onGeneratorDestroyed(self, generatorsLeft):
        pass
