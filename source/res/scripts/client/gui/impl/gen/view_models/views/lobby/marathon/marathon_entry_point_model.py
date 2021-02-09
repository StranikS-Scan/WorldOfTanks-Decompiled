# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/marathon/marathon_entry_point_model.py
from frameworks.wulf import ViewModel

class MarathonEntryPointModel(ViewModel):
    __slots__ = ('onClick',)
    STATE_MARATHON_DISABLED = -1
    STATE_MARATHON_NOT_STARTED = 0
    STATE_MARATHON_IN_PROGRESS = 1
    STATE_MARATHON_FINISHED = 3

    def __init__(self, properties=6, commands=1):
        super(MarathonEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getNumber(0)

    def setState(self, value):
        self._setNumber(0, value)

    def getTimeTillNextState(self):
        return self._getNumber(1)

    def setTimeTillNextState(self, value):
        self._setNumber(1, value)

    def getFormattedTimeTillNextState(self):
        return self._getString(2)

    def setFormattedTimeTillNextState(self, value):
        self._setString(2, value)

    def getCurrentPhase(self):
        return self._getNumber(3)

    def setCurrentPhase(self, value):
        self._setNumber(3, value)

    def getRewardObtained(self):
        return self._getBool(4)

    def setRewardObtained(self, value):
        self._setBool(4, value)

    def getDiscount(self):
        return self._getNumber(5)

    def setDiscount(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(MarathonEntryPointModel, self)._initialize()
        self._addNumberProperty('state', -1)
        self._addNumberProperty('timeTillNextState', -1)
        self._addStringProperty('formattedTimeTillNextState', '')
        self._addNumberProperty('currentPhase', -1)
        self._addBoolProperty('rewardObtained', False)
        self._addNumberProperty('discount', 0)
        self.onClick = self._addCommand('onClick')
