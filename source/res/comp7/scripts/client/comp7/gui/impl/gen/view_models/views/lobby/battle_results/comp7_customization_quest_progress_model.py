# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/battle_results/comp7_customization_quest_progress_model.py
from frameworks.wulf import ViewModel

class Comp7CustomizationQuestProgressModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(Comp7CustomizationQuestProgressModel, self).__init__(properties=properties, commands=commands)

    def getIsCompleted(self):
        return self._getBool(0)

    def setIsCompleted(self, value):
        self._setBool(0, value)

    def getCurrentProgress(self):
        return self._getNumber(1)

    def setCurrentProgress(self, value):
        self._setNumber(1, value)

    def getTotalProgress(self):
        return self._getNumber(2)

    def setTotalProgress(self, value):
        self._setNumber(2, value)

    def getEarned(self):
        return self._getNumber(3)

    def setEarned(self, value):
        self._setNumber(3, value)

    def getDescription(self):
        return self._getString(4)

    def setDescription(self, value):
        self._setString(4, value)

    def getIconKey(self):
        return self._getString(5)

    def setIconKey(self, value):
        self._setString(5, value)

    def getCustomizationId(self):
        return self._getNumber(6)

    def setCustomizationId(self, value):
        self._setNumber(6, value)

    def getCustomizationIconKey(self):
        return self._getString(7)

    def setCustomizationIconKey(self, value):
        self._setString(7, value)

    def getProgressionLevel(self):
        return self._getNumber(8)

    def setProgressionLevel(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(Comp7CustomizationQuestProgressModel, self)._initialize()
        self._addBoolProperty('isCompleted', False)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalProgress', 0)
        self._addNumberProperty('earned', 0)
        self._addStringProperty('description', '')
        self._addStringProperty('iconKey', '')
        self._addNumberProperty('customizationId', 0)
        self._addStringProperty('customizationIconKey', '')
        self._addNumberProperty('progressionLevel', 0)
