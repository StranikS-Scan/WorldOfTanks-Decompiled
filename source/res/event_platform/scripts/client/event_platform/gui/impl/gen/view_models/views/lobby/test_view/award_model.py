# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/event_platform/gui/impl/gen/view_models/views/lobby/test_view/award_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class AwardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(AwardModel, self).__init__(properties=properties, commands=commands)

    def getAwardId(self):
        return self._getNumber(0)

    def setAwardId(self, value):
        self._setNumber(0, value)

    def getAwardName(self):
        return self._getString(1)

    def setAwardName(self, value):
        self._setString(1, value)

    def getAwardIcon(self):
        return self._getResource(2)

    def setAwardIcon(self, value):
        self._setResource(2, value)

    def getAwardFlag(self):
        return self._getBool(3)

    def setAwardFlag(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(AwardModel, self)._initialize()
        self._addNumberProperty('awardId', 0)
        self._addStringProperty('awardName', '')
        self._addResourceProperty('awardIcon', R.invalid())
        self._addBoolProperty('awardFlag', False)
