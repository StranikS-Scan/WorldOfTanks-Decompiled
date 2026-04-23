# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/widgets/quests_view_model.py
from frameworks.wulf import Array, ViewModel
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel

class QuestsViewModel(ViewModel):
    __slots__ = ('onClick', 'onMarkAsViewed')

    def __init__(self, properties=13, commands=2):
        super(QuestsViewModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getConditionName(self):
        return self._getString(1)

    def setConditionName(self, value):
        self._setString(1, value)

    def getResetTime(self):
        return self._getNumber(2)

    def setResetTime(self, value):
        self._setNumber(2, value)

    def getName(self):
        return self._getString(3)

    def setName(self, value):
        self._setString(3, value)

    def getDescription(self):
        return self._getString(4)

    def setDescription(self, value):
        self._setString(4, value)

    def getIsCompleted(self):
        return self._getBool(5)

    def setIsCompleted(self, value):
        self._setBool(5, value)

    def getIsHidden(self):
        return self._getBool(6)

    def setIsHidden(self, value):
        self._setBool(6, value)

    def getAllDailyCompleted(self):
        return self._getBool(7)

    def setAllDailyCompleted(self, value):
        self._setBool(7, value)

    def getCurrentProgress(self):
        return self._getNumber(8)

    def setCurrentProgress(self, value):
        self._setNumber(8, value)

    def getMaximumProgress(self):
        return self._getNumber(9)

    def setMaximumProgress(self, value):
        self._setNumber(9, value)

    def getEarned(self):
        return self._getNumber(10)

    def setEarned(self, value):
        self._setNumber(10, value)

    def getAnimateCompletion(self):
        return self._getBool(11)

    def setAnimateCompletion(self, value):
        self._setBool(11, value)

    def getBonuses(self):
        return self._getArray(12)

    def setBonuses(self, value):
        self._setArray(12, value)

    @staticmethod
    def getBonusesType():
        return BonusItemViewModel

    def _initialize(self):
        super(QuestsViewModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('conditionName', '')
        self._addNumberProperty('resetTime', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('isHidden', False)
        self._addBoolProperty('allDailyCompleted', False)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('maximumProgress', 0)
        self._addNumberProperty('earned', 0)
        self._addBoolProperty('animateCompletion', False)
        self._addArrayProperty('bonuses', Array())
        self.onClick = self._addCommand('onClick')
        self.onMarkAsViewed = self._addCommand('onMarkAsViewed')
