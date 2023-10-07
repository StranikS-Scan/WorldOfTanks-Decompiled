# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/learning_data_model.py
from frameworks.wulf import ViewModel

class LearningDataModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(LearningDataModel, self).__init__(properties=properties, commands=commands)

    def getCrewXpAmount(self):
        return self._getNumber(0)

    def setCrewXpAmount(self, value):
        self._setNumber(0, value)

    def getPersonalXpAmount(self):
        return self._getNumber(1)

    def setPersonalXpAmount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(LearningDataModel, self)._initialize()
        self._addNumberProperty('crewXpAmount', 0)
        self._addNumberProperty('personalXpAmount', 0)
