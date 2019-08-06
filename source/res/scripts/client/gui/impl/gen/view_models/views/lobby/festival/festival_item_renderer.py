# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_item_renderer.py
from gui.impl.gen.view_models.views.lobby.festival.base_festival_item_renderer import BaseFestivalItemRenderer

class FestivalItemRenderer(BaseFestivalItemRenderer):
    __slots__ = ()

    def getReceived(self):
        return self._getBool(3)

    def setReceived(self, value):
        self._setBool(3, value)

    def getTypeOfReceived(self):
        return self._getString(4)

    def setTypeOfReceived(self, value):
        self._setString(4, value)

    def getIsInPlayerCard(self):
        return self._getBool(5)

    def setIsInPlayerCard(self, value):
        self._setBool(5, value)

    def getIsCanBuy(self):
        return self._getBool(6)

    def setIsCanBuy(self, value):
        self._setBool(6, value)

    def getIsAlternative(self):
        return self._getBool(7)

    def setIsAlternative(self, value):
        self._setBool(7, value)

    def getUnseen(self):
        return self._getBool(8)

    def setUnseen(self, value):
        self._setBool(8, value)

    def getCost(self):
        return self._getNumber(9)

    def setCost(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(FestivalItemRenderer, self)._initialize()
        self._addBoolProperty('received', False)
        self._addStringProperty('typeOfReceived', '')
        self._addBoolProperty('isInPlayerCard', False)
        self._addBoolProperty('isCanBuy', False)
        self._addBoolProperty('isAlternative', False)
        self._addBoolProperty('unseen', False)
        self._addNumberProperty('cost', -1)
