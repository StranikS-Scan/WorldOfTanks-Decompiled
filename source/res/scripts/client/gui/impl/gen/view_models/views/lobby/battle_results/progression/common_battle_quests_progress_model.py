# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/progression/common_battle_quests_progress_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.battle_results.progression.common_battle_quest_progress_model import CommonBattleQuestProgressModel

class CommonBattleQuestsProgressModel(ViewModel):
    __slots__ = ('onNavigate',)
    PATH = 'coui://gui/gameface/_dist/production/mono/plugins/post_battle/common_quests/common_quests.js'

    def __init__(self, properties=1, commands=1):
        super(CommonBattleQuestsProgressModel, self).__init__(properties=properties, commands=commands)

    def getCommonQuests(self):
        return self._getArray(0)

    def setCommonQuests(self, value):
        self._setArray(0, value)

    @staticmethod
    def getCommonQuestsType():
        return CommonBattleQuestProgressModel

    def _initialize(self):
        super(CommonBattleQuestsProgressModel, self)._initialize()
        self._addArrayProperty('commonQuests', Array())
        self.onNavigate = self._addCommand('onNavigate')
