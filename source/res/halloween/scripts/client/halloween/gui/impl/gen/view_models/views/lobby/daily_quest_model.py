# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/daily_quest_model.py
from frameworks.wulf import ViewModel

class DailyQuestModel(ViewModel):
    __slots__ = ('onGetBonusClick',)

    def __init__(self, properties=6, commands=1):
        super(DailyQuestModel, self).__init__(properties=properties, commands=commands)

    def getAbilityIcon(self):
        return self._getString(0)

    def setAbilityIcon(self, value):
        self._setString(0, value)

    def getAbilityName(self):
        return self._getString(1)

    def setAbilityName(self, value):
        self._setString(1, value)

    def getTimeInSeconds(self):
        return self._getNumber(2)

    def setTimeInSeconds(self, value):
        self._setNumber(2, value)

    def getIsBonusGot(self):
        return self._getBool(3)

    def setIsBonusGot(self, value):
        self._setBool(3, value)

    def getNumberOfBoostersAward(self):
        return self._getNumber(4)

    def setNumberOfBoostersAward(self, value):
        self._setNumber(4, value)

    def getIsShown(self):
        return self._getBool(5)

    def setIsShown(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(DailyQuestModel, self)._initialize()
        self._addStringProperty('abilityIcon', '')
        self._addStringProperty('abilityName', '')
        self._addNumberProperty('timeInSeconds', 0)
        self._addBoolProperty('isBonusGot', False)
        self._addNumberProperty('numberOfBoostersAward', 0)
        self._addBoolProperty('isShown', True)
        self.onGetBonusClick = self._addCommand('onGetBonusClick')
