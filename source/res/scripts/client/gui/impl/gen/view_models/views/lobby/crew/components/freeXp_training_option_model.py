# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/components/freeXp_training_option_model.py
from gui.impl.gen.view_models.views.lobby.crew.components.training_option_model import TrainingOptionModel

class FreeXpTrainingOptionModel(TrainingOptionModel):
    __slots__ = ('onManualInput',)

    def __init__(self, properties=8, commands=3):
        super(FreeXpTrainingOptionModel, self).__init__(properties=properties, commands=commands)

    def getPlayerXp(self):
        return self._getNumber(3)

    def setPlayerXp(self, value):
        self._setNumber(3, value)

    def getDiscountSize(self):
        return self._getNumber(4)

    def setDiscountSize(self, value):
        self._setNumber(4, value)

    def getCurrentXpValue(self):
        return self._getNumber(5)

    def setCurrentXpValue(self, value):
        self._setNumber(5, value)

    def getCurrentMaxValue(self):
        return self._getNumber(6)

    def setCurrentMaxValue(self, value):
        self._setNumber(6, value)

    def getExchangeRate(self):
        return self._getNumber(7)

    def setExchangeRate(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(FreeXpTrainingOptionModel, self)._initialize()
        self._addNumberProperty('playerXp', 0)
        self._addNumberProperty('discountSize', 0)
        self._addNumberProperty('currentXpValue', 0)
        self._addNumberProperty('currentMaxValue', 0)
        self._addNumberProperty('exchangeRate', 1)
        self.onManualInput = self._addCommand('onManualInput')
