# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mode_selector/mode_selector_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_model import ModeSelectorCardModel

class ModeSelectorModel(ViewModel):
    __slots__ = ('onItemClicked', 'onShowMapSelectionClicked', 'onShowWidgetsClicked', 'onInfoClicked')

    def __init__(self, properties=6, commands=4):
        super(ModeSelectorModel, self).__init__(properties=properties, commands=commands)

    def getIsContentVisible(self):
        return self._getBool(0)

    def setIsContentVisible(self, value):
        self._setBool(0, value)

    def getIsMapSelectionVisible(self):
        return self._getBool(1)

    def setIsMapSelectionVisible(self, value):
        self._setBool(1, value)

    def getIsMapSelectionEnabled(self):
        return self._getBool(2)

    def setIsMapSelectionEnabled(self, value):
        self._setBool(2, value)

    def getState(self):
        return self._getNumber(3)

    def setState(self, value):
        self._setNumber(3, value)

    def getAreWidgetsVisible(self):
        return self._getBool(4)

    def setAreWidgetsVisible(self, value):
        self._setBool(4, value)

    def getCardList(self):
        return self._getArray(5)

    def setCardList(self, value):
        self._setArray(5, value)

    @staticmethod
    def getCardListType():
        return ModeSelectorCardModel

    def _initialize(self):
        super(ModeSelectorModel, self)._initialize()
        self._addBoolProperty('isContentVisible', True)
        self._addBoolProperty('isMapSelectionVisible', False)
        self._addBoolProperty('isMapSelectionEnabled', False)
        self._addNumberProperty('state', 0)
        self._addBoolProperty('areWidgetsVisible', False)
        self._addArrayProperty('cardList', Array())
        self.onItemClicked = self._addCommand('onItemClicked')
        self.onShowMapSelectionClicked = self._addCommand('onShowMapSelectionClicked')
        self.onShowWidgetsClicked = self._addCommand('onShowWidgetsClicked')
        self.onInfoClicked = self._addCommand('onInfoClicked')
