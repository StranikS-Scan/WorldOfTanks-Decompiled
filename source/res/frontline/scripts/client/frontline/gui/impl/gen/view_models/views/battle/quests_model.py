# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/battle/quests_model.py
from frameworks.wulf import ViewModel

class QuestsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(QuestsModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getString(0)

    def setDescription(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getProgressGoal(self):
        return self._getNumber(2)

    def setProgressGoal(self, value):
        self._setNumber(2, value)

    def getProgressValue(self):
        return self._getNumber(3)

    def setProgressValue(self, value):
        self._setNumber(3, value)

    def getIsCompleted(self):
        return self._getBool(4)

    def setIsCompleted(self, value):
        self._setBool(4, value)

    def getIsObserver(self):
        return self._getBool(5)

    def setIsObserver(self, value):
        self._setBool(5, value)

    def getBlockDescription(self):
        return self._getString(6)

    def setBlockDescription(self, value):
        self._setString(6, value)

    def getDirectionName(self):
        return self._getString(7)

    def setDirectionName(self, value):
        self._setString(7, value)

    def getButtonKey(self):
        return self._getString(8)

    def setButtonKey(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(QuestsModel, self)._initialize()
        self._addStringProperty('description', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('progressGoal', 1)
        self._addNumberProperty('progressValue', 0)
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('isObserver', False)
        self._addStringProperty('blockDescription', '')
        self._addStringProperty('directionName', '')
        self._addStringProperty('buttonKey', '')
