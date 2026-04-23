# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/front_panel_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.front_model import FrontModel

class FrontPanelModel(ViewModel):
    __slots__ = ('onClose', 'onAboutClick', 'onFrontClick')

    def __init__(self, properties=3, commands=3):
        super(FrontPanelModel, self).__init__(properties=properties, commands=commands)

    def getSelectedFront(self):
        return self._getString(0)

    def setSelectedFront(self, value):
        self._setString(0, value)

    def getIsDisabled(self):
        return self._getBool(1)

    def setIsDisabled(self, value):
        self._setBool(1, value)

    def getFronts(self):
        return self._getArray(2)

    def setFronts(self, value):
        self._setArray(2, value)

    @staticmethod
    def getFrontsType():
        return FrontModel

    def _initialize(self):
        super(FrontPanelModel, self)._initialize()
        self._addStringProperty('selectedFront', '')
        self._addBoolProperty('isDisabled', False)
        self._addArrayProperty('fronts', Array())
        self.onClose = self._addCommand('onClose')
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onFrontClick = self._addCommand('onFrontClick')
