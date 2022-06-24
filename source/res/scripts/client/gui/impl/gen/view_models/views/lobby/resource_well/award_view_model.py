# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/resource_well/award_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class AwardViewModel(ViewModel):
    __slots__ = ('showInHangar',)

    def __init__(self, properties=2, commands=1):
        super(AwardViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    def getPersonalNumber(self):
        return self._getString(1)

    def setPersonalNumber(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(AwardViewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addStringProperty('personalNumber', '')
        self.showInHangar = self._addCommand('showInHangar')
