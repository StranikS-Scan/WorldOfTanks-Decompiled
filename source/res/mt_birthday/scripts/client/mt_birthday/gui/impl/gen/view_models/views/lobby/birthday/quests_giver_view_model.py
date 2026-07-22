# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/quests_giver_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.mt_birthday_quest_model import MtBirthdayQuestModel

class QuestsGiverViewModel(ViewModel):
    __slots__ = ('onTabVisited', 'onSoundClick', 'onTabActivate')
    ASSIGNMENTS = 0
    CHALLENGE = 1

    def __init__(self, properties=11, commands=3):
        super(QuestsGiverViewModel, self).__init__(properties=properties, commands=commands)

    def getTimeUpdate(self):
        return self._getNumber(0)

    def setTimeUpdate(self, value):
        self._setNumber(0, value)

    def getTimeNewQuest(self):
        return self._getNumber(1)

    def setTimeNewQuest(self, value):
        self._setNumber(1, value)

    def getDefaultTab(self):
        return self._getNumber(2)

    def setDefaultTab(self, value):
        self._setNumber(2, value)

    def getBattleTypes(self):
        return self._getArray(3)

    def setBattleTypes(self, value):
        self._setArray(3, value)

    @staticmethod
    def getBattleTypesType():
        return int

    def getMinLevel(self):
        return self._getNumber(4)

    def setMinLevel(self, value):
        self._setNumber(4, value)

    def getMaxLevel(self):
        return self._getNumber(5)

    def setMaxLevel(self, value):
        self._setNumber(5, value)

    def getAssignmentsQuests(self):
        return self._getArray(6)

    def setAssignmentsQuests(self, value):
        self._setArray(6, value)

    @staticmethod
    def getAssignmentsQuestsType():
        return MtBirthdayQuestModel

    def getChallengeQuests(self):
        return self._getArray(7)

    def setChallengeQuests(self, value):
        self._setArray(7, value)

    @staticmethod
    def getChallengeQuestsType():
        return MtBirthdayQuestModel

    def getIsQuestsError(self):
        return self._getBool(8)

    def setIsQuestsError(self, value):
        self._setBool(8, value)

    def getIsQuestGiverError(self):
        return self._getBool(9)

    def setIsQuestGiverError(self, value):
        self._setBool(9, value)

    def getIsSoundAnimationActive(self):
        return self._getBool(10)

    def setIsSoundAnimationActive(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(QuestsGiverViewModel, self)._initialize()
        self._addNumberProperty('timeUpdate', 1000000)
        self._addNumberProperty('timeNewQuest', 1000000)
        self._addNumberProperty('defaultTab', 0)
        self._addArrayProperty('battleTypes', Array())
        self._addNumberProperty('minLevel', 0)
        self._addNumberProperty('maxLevel', 0)
        self._addArrayProperty('assignmentsQuests', Array())
        self._addArrayProperty('challengeQuests', Array())
        self._addBoolProperty('isQuestsError', False)
        self._addBoolProperty('isQuestGiverError', False)
        self._addBoolProperty('isSoundAnimationActive', False)
        self.onTabVisited = self._addCommand('onTabVisited')
        self.onSoundClick = self._addCommand('onSoundClick')
        self.onTabActivate = self._addCommand('onTabActivate')
