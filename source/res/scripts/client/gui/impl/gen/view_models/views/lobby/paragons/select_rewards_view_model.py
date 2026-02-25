# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/select_rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.paragons.common.paragons_vehicle_model import ParagonsVehicleModel
from gui.impl.gen.view_models.views.lobby.paragons.common.request_status_model import RequestStatusModel

class SelectRewardsViewModel(ViewModel):
    __slots__ = ('onClaim', 'onClose', 'onPreview', 'onCompare')

    def __init__(self, properties=4, commands=4):
        super(SelectRewardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def requestStatus(self):
        return self._getViewModel(0)

    @staticmethod
    def getRequestStatusType():
        return RequestStatusModel

    def getAvailableToSelect(self):
        return self._getNumber(1)

    def setAvailableToSelect(self, value):
        self._setNumber(1, value)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def getAvailableRewards(self):
        return self._getArray(3)

    def setAvailableRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getAvailableRewardsType():
        return ParagonsVehicleModel

    def _initialize(self):
        super(SelectRewardsViewModel, self)._initialize()
        self._addViewModelProperty('requestStatus', RequestStatusModel())
        self._addNumberProperty('availableToSelect', 0)
        self._addNumberProperty('level', 0)
        self._addArrayProperty('availableRewards', Array())
        self.onClaim = self._addCommand('onClaim')
        self.onClose = self._addCommand('onClose')
        self.onPreview = self._addCommand('onPreview')
        self.onCompare = self._addCommand('onCompare')
