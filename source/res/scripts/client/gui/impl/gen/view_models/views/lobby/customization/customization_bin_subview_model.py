# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_bin_subview_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.customization.cart_season_model import CartSeasonModel

class CustomizationBinSubviewModel(ViewModel):
    __slots__ = ('onCloseAction', 'onSelectItem', 'onTutorialClose')

    def __init__(self, properties=5, commands=3):
        super(CustomizationBinSubviewModel, self).__init__(properties=properties, commands=commands)

    def getIsShown(self):
        return self._getBool(0)

    def setIsShown(self, value):
        self._setBool(0, value)

    def getIsAnySelected(self):
        return self._getBool(1)

    def setIsAnySelected(self, value):
        self._setBool(1, value)

    def getIsRendererPipelineDeferred(self):
        return self._getBool(2)

    def setIsRendererPipelineDeferred(self, value):
        self._setBool(2, value)

    def getSelectedSeason(self):
        return self._getString(3)

    def setSelectedSeason(self, value):
        self._setString(3, value)

    def getSeasons(self):
        return self._getArray(4)

    def setSeasons(self, value):
        self._setArray(4, value)

    @staticmethod
    def getSeasonsType():
        return CartSeasonModel

    def _initialize(self):
        super(CustomizationBinSubviewModel, self)._initialize()
        self._addBoolProperty('isShown', False)
        self._addBoolProperty('isAnySelected', False)
        self._addBoolProperty('isRendererPipelineDeferred', False)
        self._addStringProperty('selectedSeason', '')
        self._addArrayProperty('seasons', Array())
        self.onCloseAction = self._addCommand('onCloseAction')
        self.onSelectItem = self._addCommand('onSelectItem')
        self.onTutorialClose = self._addCommand('onTutorialClose')
