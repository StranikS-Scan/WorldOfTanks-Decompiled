# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/assign_to_vehicle_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.detachment.common.auto_scroll_model import AutoScrollModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_card_model import DetachmentCardModel
from gui.impl.gen.view_models.views.lobby.detachment.common.filters_model import FiltersModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.popover_tracker_impl_model import PopoverTrackerImplModel
from gui.impl.gen.view_models.views.lobby.detachment.common.ttc_model import TtcModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel

class AssignToVehicleViewModel(NavigationViewModel):
    __slots__ = ('onMobilizeClick', 'onRecruitBtnClick', 'onDetachmentCardClick', 'onDetachmentRecoverClick', 'onDetachmentCardHover', 'onDetachmentCardOut')

    def __init__(self, properties=10, commands=9):
        super(AssignToVehicleViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleModel(self):
        return self._getViewModel(2)

    @property
    def filtersModel(self):
        return self._getViewModel(3)

    @property
    def popover(self):
        return self._getViewModel(4)

    @property
    def ttcModel(self):
        return self._getViewModel(5)

    @property
    def autoScroll(self):
        return self._getViewModel(6)

    def getAvailableForConvert(self):
        return self._getNumber(7)

    def setAvailableForConvert(self, value):
        self._setNumber(7, value)

    def getEndTimeConvert(self):
        return self._getNumber(8)

    def setEndTimeConvert(self, value):
        self._setNumber(8, value)

    def getDetachmentList(self):
        return self._getArray(9)

    def setDetachmentList(self, value):
        self._setArray(9, value)

    def _initialize(self):
        super(AssignToVehicleViewModel, self)._initialize()
        self._addViewModelProperty('vehicleModel', VehicleModel())
        self._addViewModelProperty('filtersModel', FiltersModel())
        self._addViewModelProperty('popover', PopoverTrackerImplModel())
        self._addViewModelProperty('ttcModel', TtcModel())
        self._addViewModelProperty('autoScroll', AutoScrollModel())
        self._addNumberProperty('availableForConvert', 0)
        self._addNumberProperty('endTimeConvert', 0)
        self._addArrayProperty('detachmentList', Array())
        self.onMobilizeClick = self._addCommand('onMobilizeClick')
        self.onRecruitBtnClick = self._addCommand('onRecruitBtnClick')
        self.onDetachmentCardClick = self._addCommand('onDetachmentCardClick')
        self.onDetachmentRecoverClick = self._addCommand('onDetachmentRecoverClick')
        self.onDetachmentCardHover = self._addCommand('onDetachmentCardHover')
        self.onDetachmentCardOut = self._addCommand('onDetachmentCardOut')
