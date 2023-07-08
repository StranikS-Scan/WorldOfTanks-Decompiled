# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/sub_modes/qfg_sub_mode.py
import typing
from fun_random.gui.feature.sub_modes.base_sub_mode import FunBaseSubMode
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
if typing.TYPE_CHECKING:
    from fun_random.gui.vehicle_view_states import FunRandomVehicleViewState
    from gui.shared.utils.requesters import RequestCriteria

class FunQuickFireGunsSubMode(FunBaseSubMode):

    def getCarouselBaseCriteria(self):
        return REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.FUN_RANDOM | REQ_CRITERIA.VEHICLE.MODE_HIDDEN

    def resolveVehicleViewState(self, viewState):
        viewState.setLevelShown(False)
        viewState.setRoleShown(False)
