# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/quest_progresive_model.py
from frameworks.wulf import ViewModel

class QuestProgresiveModel(ViewModel):
    __slots__ = ('onAnimationCompleted',)

    def __init__(self, properties=9, commands=1):
        super(QuestProgresiveModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getNameQuest(self):
        return self._getString(1)

    def setNameQuest(self, value):
        self._setString(1, value)

    def getDescriptionQuest(self):
        return self._getString(2)

    def setDescriptionQuest(self, value):
        self._setString(2, value)

    def getNameRole(self):
        return self._getString(3)

    def setNameRole(self, value):
        self._setString(3, value)

    def getDescriptionRole(self):
        return self._getString(4)

    def setDescriptionRole(self, value):
        self._setString(4, value)

    def getCurrentProgress(self):
        return self._getNumber(5)

    def setCurrentProgress(self, value):
        self._setNumber(5, value)

    def getPreviousProgress(self):
        return self._getNumber(6)

    def setPreviousProgress(self, value):
        self._setNumber(6, value)

    def getMaxProgress(self):
        return self._getNumber(7)

    def setMaxProgress(self, value):
        self._setNumber(7, value)

    def getIsCompleted(self):
        return self._getBool(8)

    def setIsCompleted(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(QuestProgresiveModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('nameQuest', '')
        self._addStringProperty('descriptionQuest', '')
        self._addStringProperty('nameRole', '')
        self._addStringProperty('descriptionRole', '')
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('previousProgress', 0)
        self._addNumberProperty('maxProgress', 0)
        self._addBoolProperty('isCompleted', False)
        self.onAnimationCompleted = self._addCommand('onAnimationCompleted')
