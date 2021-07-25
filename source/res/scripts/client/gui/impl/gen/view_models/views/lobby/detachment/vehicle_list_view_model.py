# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/vehicle_list_view_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.detachment.common.detachment_short_info_model import DetachmentShortInfoModel
from gui.impl.gen.view_models.views.lobby.detachment.common.filters_model import FiltersModel
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.popover_tracker_impl_model import PopoverTrackerImplModel
from gui.impl.gen.view_models.views.lobby.detachment.common.ttc_model import TtcModel
from gui.impl.gen.view_models.views.lobby.detachment.vehicle_card_model import VehicleCardModel

class VehicleListViewModel(NavigationViewModel):
    __slots__ = ('onItemHover', 'onItemClick')

    def __init__(self, properties=8, commands=5):
        super(VehicleListViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def filtersModel(self):
        return self._getViewModel(2)

    @property
    def popover(self):
        return self._getViewModel(3)

    @property
    def detachmentInfo(self):
        return self._getViewModel(4)

    @property
    def vehicles(self):
        return self._getViewModel(5)

    @property
    def ttcModel(self):
        return self._getViewModel(6)

    def getSelectedVehicleName(self):
        return self._getString(7)

    def setSelectedVehicleName(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(VehicleListViewModel, self)._initialize()
        self._addViewModelProperty('filtersModel', FiltersModel())
        self._addViewModelProperty('popover', PopoverTrackerImplModel())
        self._addViewModelProperty('detachmentInfo', DetachmentShortInfoModel())
        self._addViewModelProperty('vehicles', UserListModel())
        self._addViewModelProperty('ttcModel', TtcModel())
        self._addStringProperty('selectedVehicleName', '')
        self.onItemHover = self._addCommand('onItemHover')
        self.onItemClick = self._addCommand('onItemClick')
