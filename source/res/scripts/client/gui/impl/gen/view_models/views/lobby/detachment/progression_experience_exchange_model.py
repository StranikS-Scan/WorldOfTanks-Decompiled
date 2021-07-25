# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/progression_experience_exchange_model.py
from frameworks.wulf import ViewModel

class ProgressionExperienceExchangeModel(ViewModel):
    __slots__ = ('onStepperValueChange', 'onSubmitExchange')

    def __init__(self, properties=5, commands=2):
        super(ProgressionExperienceExchangeModel, self).__init__(properties=properties, commands=commands)

    def getAvailableFreeExp(self):
        return self._getNumber(0)

    def setAvailableFreeExp(self, value):
        self._setNumber(0, value)

    def getRate(self):
        return self._getNumber(1)

    def setRate(self, value):
        self._setNumber(1, value)

    def getExpToNextLvl(self):
        return self._getNumber(2)

    def setExpToNextLvl(self, value):
        self._setNumber(2, value)

    def getIsMaxLevelDetachment(self):
        return self._getBool(3)

    def setIsMaxLevelDetachment(self, value):
        self._setBool(3, value)

    def getIsLastLevelToElite(self):
        return self._getBool(4)

    def setIsLastLevelToElite(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(ProgressionExperienceExchangeModel, self)._initialize()
        self._addNumberProperty('availableFreeExp', 0)
        self._addNumberProperty('rate', 0)
        self._addNumberProperty('expToNextLvl', 0)
        self._addBoolProperty('isMaxLevelDetachment', False)
        self._addBoolProperty('isLastLevelToElite', False)
        self.onStepperValueChange = self._addCommand('onStepperValueChange')
        self.onSubmitExchange = self._addCommand('onSubmitExchange')
