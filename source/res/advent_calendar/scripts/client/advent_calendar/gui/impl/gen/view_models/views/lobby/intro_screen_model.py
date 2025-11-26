# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/gen/view_models/views/lobby/intro_screen_model.py
from frameworks.wulf import ViewModel

class IntroScreenModel(ViewModel):
    __slots__ = ('onClose', 'onCloseAnimationStarted')

    def __init__(self, properties=5, commands=2):
        super(IntroScreenModel, self).__init__(properties=properties, commands=commands)

    def getStartDate(self):
        return self._getNumber(0)

    def setStartDate(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getDoorsCount(self):
        return self._getNumber(2)

    def setDoorsCount(self, value):
        self._setNumber(2, value)

    def getIsOpenedFirstTime(self):
        return self._getBool(3)

    def setIsOpenedFirstTime(self, value):
        self._setBool(3, value)

    def getIsAnimationEnabled(self):
        return self._getBool(4)

    def setIsAnimationEnabled(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(IntroScreenModel, self)._initialize()
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('doorsCount', 0)
        self._addBoolProperty('isOpenedFirstTime', False)
        self._addBoolProperty('isAnimationEnabled', False)
        self.onClose = self._addCommand('onClose')
        self.onCloseAnimationStarted = self._addCommand('onCloseAnimationStarted')
