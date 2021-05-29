# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/blueprints/blueprint_price_content_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_value_price import BlueprintValuePrice

class BlueprintPriceContentModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(BlueprintPriceContentModel, self).__init__(properties=properties, commands=commands)

    @property
    def valueMain(self):
        return self._getViewModel(0)

    @property
    def additionalValues(self):
        return self._getViewModel(1)

    def getTooltipId(self):
        return self._getNumber(2)

    def setTooltipId(self, value):
        self._setNumber(2, value)

    def getHasAdditionalCost(self):
        return self._getBool(3)

    def setHasAdditionalCost(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(BlueprintPriceContentModel, self)._initialize()
        self._addViewModelProperty('valueMain', BlueprintValuePrice())
        self._addViewModelProperty('additionalValues', ListModel())
        self._addNumberProperty('tooltipId', 0)
        self._addBoolProperty('hasAdditionalCost', False)
