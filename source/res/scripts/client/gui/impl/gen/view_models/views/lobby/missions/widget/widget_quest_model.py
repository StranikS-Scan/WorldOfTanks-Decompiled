# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/missions/widget/widget_quest_model.py
from frameworks.wulf import ViewModel

class WidgetQuestModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
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

    def getEarned(self):
        return self._getNumber(5)

    def setEarned(self, value):
        self._setNumber(5, value)

    def getDescription(self):
        return self._getString(6)

    def setDescription(self, value):
        self._setString(6, value)

    def getCompletedCount(self):
        return self._getNumber(7)

    def setCompletedCount(self, value):
        self._setNumber(7, value)

    def getTotalCount(self):
        return self._getNumber(8)

    def setTotalCount(self, value):
        self._setNumber(8, value)

    def getIsRTS(self):
        return self._getBool(9)

    def setIsRTS(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(WidgetQuestModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('icon', '')
        self._addBoolProperty('completed', False)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalProgress', 0)
        self._addNumberProperty('earned', 0)
        self._addStringProperty('description', '')
        self._addNumberProperty('completedCount', 0)
        self._addNumberProperty('totalCount', 1)
        self._addBoolProperty('isRTS', False)
