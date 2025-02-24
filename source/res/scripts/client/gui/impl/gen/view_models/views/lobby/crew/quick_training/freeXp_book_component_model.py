# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/quick_training/freeXp_book_component_model.py
from gui.impl.gen.view_models.views.lobby.crew.components.component_base_model import ComponentBaseModel

class FreeXpBookComponentModel(ComponentBaseModel):
    __slots__ = ('mouseEnter', 'select', 'update', 'manualInput')

    def __init__(self, properties=7, commands=4):
        super(FreeXpBookComponentModel, self).__init__(properties=properties, commands=commands)

    def getCurrentXpValue(self):
        return self._getNumber(1)

    def setCurrentXpValue(self, value):
        self._setNumber(1, value)

    def getMaxXpValue(self):
        return self._getNumber(2)

    def setMaxXpValue(self, value):
        self._setNumber(2, value)

    def getDiscountSize(self):
        return self._getNumber(3)

    def setDiscountSize(self, value):
        self._setNumber(3, value)

    def getExchangeRate(self):
        return self._getNumber(4)

    def setExchangeRate(self, value):
        self._setNumber(4, value)

    def getIsDisabled(self):
        return self._getBool(5)

    def setIsDisabled(self, value):
        self._setBool(5, value)

    def getHasError(self):
        return self._getBool(6)

    def setHasError(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(FreeXpBookComponentModel, self)._initialize()
        self._addNumberProperty('currentXpValue', 0)
        self._addNumberProperty('maxXpValue', 0)
        self._addNumberProperty('discountSize', 0)
        self._addNumberProperty('exchangeRate', 1)
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('hasError', False)
        self.mouseEnter = self._addCommand('mouseEnter')
        self.select = self._addCommand('select')
        self.update = self._addCommand('update')
        self.manualInput = self._addCommand('manualInput')
