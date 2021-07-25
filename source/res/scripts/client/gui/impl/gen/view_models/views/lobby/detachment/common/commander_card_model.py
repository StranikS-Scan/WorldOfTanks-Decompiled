# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/commander_card_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.commander_model import CommanderModel

class CommanderCardModel(CommanderModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(CommanderCardModel, self).__init__(properties=properties, commands=commands)

    def getAmount(self):
        return self._getNumber(6)

    def setAmount(self, value):
        self._setNumber(6, value)

    def getState(self):
        return self._getString(7)

    def setState(self, value):
        self._setString(7, value)

    def getType(self):
        return self._getString(8)

    def setType(self, value):
        self._setString(8, value)

    def getPortraitType(self):
        return self._getString(9)

    def setPortraitType(self, value):
        self._setString(9, value)

    def getNewItemsAmount(self):
        return self._getNumber(10)

    def setNewItemsAmount(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(CommanderCardModel, self)._initialize()
        self._addNumberProperty('amount', 1)
        self._addStringProperty('state', '')
        self._addStringProperty('type', '')
        self._addStringProperty('portraitType', '')
        self._addNumberProperty('newItemsAmount', 0)
