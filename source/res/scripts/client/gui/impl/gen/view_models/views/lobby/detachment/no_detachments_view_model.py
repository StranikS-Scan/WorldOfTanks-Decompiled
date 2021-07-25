# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/no_detachments_view_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel

class NoDetachmentsViewModel(NavigationViewModel):
    __slots__ = ('onMobilizeClick', 'onRecruitBtnClick')

    def __init__(self, properties=5, commands=5):
        super(NoDetachmentsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleModel(self):
        return self._getViewModel(2)

    def getAvailableForConvert(self):
        return self._getNumber(3)

    def setAvailableForConvert(self, value):
        self._setNumber(3, value)

    def getEndTimeConvert(self):
        return self._getNumber(4)

    def setEndTimeConvert(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(NoDetachmentsViewModel, self)._initialize()
        self._addViewModelProperty('vehicleModel', VehicleModel())
        self._addNumberProperty('availableForConvert', 0)
        self._addNumberProperty('endTimeConvert', 0)
        self.onMobilizeClick = self._addCommand('onMobilizeClick')
        self.onRecruitBtnClick = self._addCommand('onRecruitBtnClick')
