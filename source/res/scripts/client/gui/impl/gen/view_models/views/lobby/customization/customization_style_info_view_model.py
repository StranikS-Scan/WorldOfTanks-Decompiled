# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_style_info_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.customization.customization_bill_base_model import CustomizationBillBaseModel
from gui.impl.gen.view_models.views.lobby.customization.customization_style_availability_model import CustomizationStyleAvailabilityModel
from gui.impl.gen.view_models.views.lobby.customization.customization_style_parameter_model import CustomizationStyleParameterModel

class CustomizationStyleInfoViewModel(ViewModel):
    __slots__ = ('onShowBuyWindow',)

    def __init__(self, properties=5, commands=1):
        super(CustomizationStyleInfoViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def billData(self):
        return self._getViewModel(0)

    @staticmethod
    def getBillDataType():
        return CustomizationBillBaseModel

    def getStyleName(self):
        return self._getString(1)

    def setStyleName(self, value):
        self._setString(1, value)

    def getStyleInfo(self):
        return self._getString(2)

    def setStyleInfo(self, value):
        self._setString(2, value)

    def getParameters(self):
        return self._getArray(3)

    def setParameters(self, value):
        self._setArray(3, value)

    @staticmethod
    def getParametersType():
        return CustomizationStyleParameterModel

    def getAvailabilityList(self):
        return self._getArray(4)

    def setAvailabilityList(self, value):
        self._setArray(4, value)

    @staticmethod
    def getAvailabilityListType():
        return CustomizationStyleAvailabilityModel

    def _initialize(self):
        super(CustomizationStyleInfoViewModel, self)._initialize()
        self._addViewModelProperty('billData', CustomizationBillBaseModel())
        self._addStringProperty('styleName', '')
        self._addStringProperty('styleInfo', '')
        self._addArrayProperty('parameters', Array())
        self._addArrayProperty('availabilityList', Array())
        self.onShowBuyWindow = self._addCommand('onShowBuyWindow')
