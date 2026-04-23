# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_header_vehicle_info_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class CustomizationHeaderVehicleInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(CustomizationHeaderVehicleInfoModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleType():
        return VehicleModel

    def getIsQuestProgressionInfoBtnVisible(self):
        return self._getBool(1)

    def setIsQuestProgressionInfoBtnVisible(self, value):
        self._setBool(1, value)

    def getIsStyleBonusPreviewText(self):
        return self._getBool(2)

    def setIsStyleBonusPreviewText(self, value):
        self._setBool(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(CustomizationHeaderVehicleInfoModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addBoolProperty('isQuestProgressionInfoBtnVisible', False)
        self._addBoolProperty('isStyleBonusPreviewText', False)
        self._addStringProperty('description', '')
