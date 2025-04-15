# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/widget_quest_model.py
from frameworks.wulf import ViewModel

class WidgetQuestModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(WidgetQuestModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getCompleted(self):
        return self._getBool(2)

    def setCompleted(self, value):
        self._setBool(2, value)

    def getCurrentProgress(self):
        return self._getNumber(3)

    def setCurrentProgress(self, value):
        self._setNumber(3, value)

    def getTotalProgress(self):
        return self._getNumber(4)

    def setTotalProgress(self, value):
        self._setNumber(4, value)

    def getHasPremium(self):
        return self._getBool(5)

    def setHasPremium(self, value):
        self._setBool(5, value)

    def getIsPremium(self):
        return self._getBool(6)

    def setIsPremium(self, value):
        self._setBool(6, value)

    def getEarned(self):
        return self._getNumber(7)

    def setEarned(self, value):
        self._setNumber(7, value)

    def getDescription(self):
        return self._getString(8)

    def setDescription(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(WidgetQuestModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('icon', '')
        self._addBoolProperty('completed', False)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalProgress', 0)
        self._addBoolProperty('hasPremium', False)
        self._addBoolProperty('isPremium', False)
        self._addNumberProperty('earned', 0)
        self._addStringProperty('description', '')
