# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/detachment/detachment_view_adaptor.py
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.lobby.detachment.assign_to_vehicle_view import AssignToVehicleView
from gui.impl.lobby.detachment.instructors_list_view import InstructorsListView
from gui.impl.lobby.detachment.mobilization_view import MobilizationView
from gui.impl.lobby.detachment.perks_matrix_view import PerksMatrixView
from gui.impl.lobby.detachment.vehicle_list_view import VehicleListView
from soft_exception import SoftException
viewNameClass = {NavigationViewModel.PERSONAL_CASE_PERKS_MATRIX: PerksMatrixView,
 NavigationViewModel.VEHICLE_LIST: VehicleListView,
 NavigationViewModel.INSTRUCTORS_LIST: InstructorsListView,
 NavigationViewModel.ASSIGN_TO_VEHICLE: AssignToVehicleView,
 NavigationViewModel.MOBILIZATION: MobilizationView}

class DetachmentViewAdaptor(InjectComponentAdaptor):

    def __init__(self, ctx):
        super(DetachmentViewAdaptor, self).__init__()
        self.__ctx = ctx

    def _makeInjectView(self):
        viewClass = viewNameClass.get(self.__ctx.get('navigationViewSettings').getViewId())
        if viewClass is not None:
            injectView = viewClass(self.__ctx)
        else:
            raise SoftException('Incorrect viewId {0}'.format(type))
        self.__ctx = None
        return injectView

    @property
    def injectView(self):
        return self._injectView
