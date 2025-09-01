# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/common/base_quest_model.py
from frameworks.wulf import ViewModel

class BaseQuestModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(BaseQuestModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getAnimationId(self):
        return self._getString(1)

    def setAnimationId(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getCurrentProgress(self):
        return self._getNumber(4)

    def setCurrentProgress(self, value):
        self._setNumber(4, value)

    def getTotalProgress(self):
        return self._getNumber(5)

    def setTotalProgress(self, value):
        self._setNumber(5, value)

    def getEarned(self):
        return self._getNumber(6)

    def setEarned(self, value):
        self._setNumber(6, value)

    def getIsCompleted(self):
        return self._getBool(7)

    def setIsCompleted(self, value):
        self._setBool(7, value)

    def getAnimateCompletion(self):
        return self._getBool(8)

    def setAnimateCompletion(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(BaseQuestModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('animationId', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('description', '')
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalProgress', 0)
        self._addNumberProperty('earned', 0)
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('animateCompletion', False)
