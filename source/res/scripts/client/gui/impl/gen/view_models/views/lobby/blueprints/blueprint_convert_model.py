# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/blueprints/blueprint_convert_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_balance_content_model import BlueprintBalanceContentModel
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_price import BlueprintPrice
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class BlueprintConvertModel(FullScreenDialogWindowModel):
    __slots__ = ('onSelectItem', 'onSliderShift')

    def __init__(self, properties=19, commands=5):
        super(BlueprintConvertModel, self).__init__(properties=properties, commands=commands)

    @property
    def fragmentsBalance(self):
        return self._getViewModel(11)

    @staticmethod
    def getFragmentsBalanceType():
        return BlueprintBalanceContentModel

    @property
    def usedMainPrice(self):
        return self._getViewModel(12)

    @staticmethod
    def getUsedMainPriceType():
        return BlueprintPrice

    def getTotalCount(self):
        return self._getNumber(13)

    def setTotalCount(self, value):
        self._setNumber(13, value)

    def getCount(self):
        return self._getNumber(14)

    def setCount(self, value):
        self._setNumber(14, value)

    def getAllianceName(self):
        return self._getString(15)

    def setAllianceName(self, value):
        self._setString(15, value)

    def getAdditionalPriceOptions(self):
        return self._getArray(16)

    def setAdditionalPriceOptions(self, value):
        self._setArray(16, value)

    @staticmethod
    def getAdditionalPriceOptionsType():
        return BlueprintPrice

    def getUsedAdditionalPrice(self):
        return self._getArray(17)

    def setUsedAdditionalPrice(self, value):
        self._setArray(17, value)

    @staticmethod
    def getUsedAdditionalPriceType():
        return BlueprintPrice

    def getSyncInitiator(self):
        return self._getNumber(18)

    def setSyncInitiator(self, value):
        self._setNumber(18, value)

    def _initialize(self):
        super(BlueprintConvertModel, self)._initialize()
        self._addViewModelProperty('fragmentsBalance', BlueprintBalanceContentModel())
        self._addViewModelProperty('usedMainPrice', BlueprintPrice())
        self._addNumberProperty('totalCount', 1)
        self._addNumberProperty('count', 1)
        self._addStringProperty('allianceName', '')
        self._addArrayProperty('additionalPriceOptions', Array())
        self._addArrayProperty('usedAdditionalPrice', Array())
        self._addNumberProperty('syncInitiator', 0)
        self.onSelectItem = self._addCommand('onSelectItem')
        self.onSliderShift = self._addCommand('onSliderShift')
