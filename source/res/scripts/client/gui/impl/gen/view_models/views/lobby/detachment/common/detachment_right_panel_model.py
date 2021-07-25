# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/detachment_right_panel_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.popover_tracker_impl_model import PopoverTrackerImplModel
from gui.impl.gen.view_models.views.lobby.detachment.common.rose_model import RoseModel
from gui.impl.gen.view_models.views.lobby.detachment.common.ttc_model import TtcModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel

class DetachmentRightPanelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DetachmentRightPanelModel, self).__init__(properties=properties, commands=commands)

    @property
    def roseModel(self):
        return self._getViewModel(0)

    @property
    def selectedVehicle(self):
        return self._getViewModel(1)

    @property
    def popover(self):
        return self._getViewModel(2)

    @property
    def ttcModel(self):
        return self._getViewModel(3)

    def _initialize(self):
        super(DetachmentRightPanelModel, self)._initialize()
        self._addViewModelProperty('roseModel', RoseModel())
        self._addViewModelProperty('selectedVehicle', VehicleModel())
        self._addViewModelProperty('popover', PopoverTrackerImplModel())
        self._addViewModelProperty('ttcModel', TtcModel())
