# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/progression/common_battle_quest_progress_model.py
from gui.impl.gen.view_models.common.missions.quest_model import QuestModel

class CommonBattleQuestProgressModel(QuestModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=0):
        super(CommonBattleQuestProgressModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(11)

    def setIcon(self, value):
        self._setString(11, value)

    def getGuiDisabled(self):
        return self._getBool(12)

    def setGuiDisabled(self, value):
        self._setBool(12, value)

    def getHidden(self):
        return self._getBool(13)

    def setHidden(self, value):
        self._setBool(13, value)

    def getAvailable(self):
        return self._getBool(14)

    def setAvailable(self, value):
        self._setBool(14, value)

    def getCurrentCompletionCount(self):
        return self._getNumber(15)

    def setCurrentCompletionCount(self, value):
        self._setNumber(15, value)

    def getMaxCompletionCount(self):
        return self._getNumber(16)

    def setMaxCompletionCount(self, value):
        self._setNumber(16, value)

    def getDefaultMaxCompletionCount(self):
        return self._getNumber(17)

    def setDefaultMaxCompletionCount(self, value):
        self._setNumber(17, value)

    def getNavigationEnabled(self):
        return self._getBool(18)

    def setNavigationEnabled(self, value):
        self._setBool(18, value)

    def _initialize(self):
        super(CommonBattleQuestProgressModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addBoolProperty('guiDisabled', False)
        self._addBoolProperty('hidden', False)
        self._addBoolProperty('available', False)
        self._addNumberProperty('currentCompletionCount', 0)
        self._addNumberProperty('maxCompletionCount', 1)
        self._addNumberProperty('defaultMaxCompletionCount', 1)
        self._addBoolProperty('navigationEnabled', False)
