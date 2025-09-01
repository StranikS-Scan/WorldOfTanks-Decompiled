# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/feature/battle_results/simplified_quests_view_model.py
from frameworks.wulf import ViewModel

class SimplifiedQuestsViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(SimplifiedQuestsViewModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(0)

    def setIcon(self, value):
        self._setString(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getIsCompleted(self):
        return self._getBool(2)

    def setIsCompleted(self, value):
        self._setBool(2, value)

    def getCurrentProgress(self):
        return self._getNumber(3)

    def setCurrentProgress(self, value):
        self._setNumber(3, value)

    def getTotalProgress(self):
        return self._getNumber(4)

    def setTotalProgress(self, value):
        self._setNumber(4, value)

    def getLastProgressValue(self):
        return self._getNumber(5)

    def setLastProgressValue(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(SimplifiedQuestsViewModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addStringProperty('description', '')
        self._addBoolProperty('isCompleted', False)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalProgress', 0)
        self._addNumberProperty('lastProgressValue', 0)
