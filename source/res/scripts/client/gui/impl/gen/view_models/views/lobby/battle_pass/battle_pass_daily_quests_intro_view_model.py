# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_daily_quests_intro_view_model.py
from frameworks.wulf import ViewModel

class BattlePassDailyQuestsIntroViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(BattlePassDailyQuestsIntroViewModel, self).__init__(properties=properties, commands=commands)

    def getQuestNumber(self):
        return self._getNumber(0)

    def setQuestNumber(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(BattlePassDailyQuestsIntroViewModel, self)._initialize()
        self._addNumberProperty('questNumber', 0)
