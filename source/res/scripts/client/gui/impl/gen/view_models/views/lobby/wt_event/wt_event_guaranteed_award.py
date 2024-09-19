# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_guaranteed_award.py
from frameworks.wulf import ViewModel

class WtEventGuaranteedAward(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(WtEventGuaranteedAward, self).__init__(properties=properties, commands=commands)

    def getAttemptsCount(self):
        return self._getNumber(0)

    def setAttemptsCount(self, value):
        self._setNumber(0, value)

    def getLeftAttemptsCount(self):
        return self._getNumber(1)

    def setLeftAttemptsCount(self, value):
        self._setNumber(1, value)

    def getGuaranteedTankAttemptCount(self):
        return self._getNumber(2)

    def setGuaranteedTankAttemptCount(self, value):
        self._setNumber(2, value)

    def getIsIgnored(self):
        return self._getBool(3)

    def setIsIgnored(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(WtEventGuaranteedAward, self)._initialize()
        self._addNumberProperty('attemptsCount', 0)
        self._addNumberProperty('leftAttemptsCount', 0)
        self._addNumberProperty('guaranteedTankAttemptCount', 0)
        self._addBoolProperty('isIgnored', False)
