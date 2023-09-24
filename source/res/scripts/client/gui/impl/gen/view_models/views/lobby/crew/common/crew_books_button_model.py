# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/crew_books_button_model.py
from gui.impl.gen.view_models.views.lobby.crew.common.button_model import ButtonModel

class CrewBooksButtonModel(ButtonModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(CrewBooksButtonModel, self).__init__(properties=properties, commands=commands)

    def getTotalAmount(self):
        return self._getNumber(1)

    def setTotalAmount(self, value):
        self._setNumber(1, value)

    def getNewAmount(self):
        return self._getNumber(2)

    def setNewAmount(self, value):
        self._setNumber(2, value)

    def getHasDiscount(self):
        return self._getBool(3)

    def setHasDiscount(self, value):
        self._setBool(3, value)

    def getIsDisabled(self):
        return self._getBool(4)

    def setIsDisabled(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(CrewBooksButtonModel, self)._initialize()
        self._addNumberProperty('totalAmount', 0)
        self._addNumberProperty('newAmount', 0)
        self._addBoolProperty('hasDiscount', False)
        self._addBoolProperty('isDisabled', False)
