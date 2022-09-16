# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/select_slot_spec_compare_dialog.py
import typing
from BWUtil import AsyncReturn
from wg_async import wg_async, wg_await
from frameworks.wulf import ViewSettings
from gui.impl.dialogs.dialogs import showSingleDialogWithResultData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.select_slot_spec_dialog_spec_model import SelectSlotSpecDialogSpecModel
from gui.impl.gen.view_models.views.lobby.vehicle_compare.select_slot_spec_compare_dialog_model import SelectSlotSpecCompareDialogModel
from gui.impl.lobby.common.select_slot_spec_dialog import SelectSlotSpecDialogMainContent
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from helpers import dependency
from items.components.supply_slot_categories import SlotCategories
from skeletons.gui.game_control import IVehicleComparisonBasket
from gui.Scaleform.Waiting import Waiting
_SLOT_IS_NOT_SELECTED_IDX = 0
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from frameworks.wulf import Window

class SelectSlotSpecCompareDialogMainContent(SelectSlotSpecDialogMainContent):

    def __init__(self, vehicle, viewModel, slotIdx=None):
        super(SelectSlotSpecCompareDialogMainContent, self).__init__(vehicle, viewModel, slotIdx)
        self._startIdx = 0

    def setAvailableSpecs(self, model, optDevices):
        slotModel = SelectSlotSpecDialogSpecModel()
        slotModel.setId(_SLOT_IS_NOT_SELECTED_IDX)
        slotModel.setSpecialization(SlotCategories.UNIVERSAL)
        model.getAvailableSpecs().addViewModel(slotModel)
        for slot in optDevices.dynSlotTypeOptions:
            slotModel = SelectSlotSpecDialogSpecModel()
            slotModel.setId(slot.slotID)
            self._fillSpecsModel(slotModel, slot.categories)
            model.getAvailableSpecs().addViewModel(slotModel)


class SelectSlotSpecCompareDialog(FullScreenDialogView):
    __slots__ = ('__vehicle', '__mainContent')
    __vehicleComparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, vehicle):
        settings = ViewSettings(R.views.lobby.vehicle_compare.SelectSlotSpecCompareDialog(), model=SelectSlotSpecCompareDialogModel())
        self.__vehicle = vehicle
        super(SelectSlotSpecCompareDialog, self).__init__(settings)
        self.__mainContent = None
        return

    @property
    def viewModel(self):
        return super(SelectSlotSpecCompareDialog, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        model = self.getViewModel()
        model.hold()
        super(SelectSlotSpecCompareDialog, self)._onLoading(*args, **kwargs)
        self.__mainContent = SelectSlotSpecCompareDialogMainContent(self.__vehicle, model.mainContent, self.__vehicle.optDevices.dynSlotTypeIdx)
        self.__mainContent.onLoading()
        model.commit()

    def _onLoaded(self, *args, **kwargs):
        super(SelectSlotSpecCompareDialog, self)._onLoaded(*args, **kwargs)
        Waiting.hide('loadModalWindow')

    def _getAdditionalData(self):
        return self.__mainContent and self.__mainContent.getSelectedSlot()

    def _initialize(self, *args, **kwargs):
        super(SelectSlotSpecCompareDialog, self)._initialize()
        if self.__mainContent:
            self.__mainContent.initialize()
        self.__vehicleComparisonBasket.onSwitchChange += self.__serverSettingsChange
        self.__vehicleComparisonBasket.onParametersChange += self.__serverSettingsChange

    def _finalize(self):
        if self.__mainContent:
            self.__mainContent.finalize()
        self.__vehicleComparisonBasket.onSwitchChange -= self.__serverSettingsChange
        self.__vehicleComparisonBasket.onParametersChange -= self.__serverSettingsChange
        super(SelectSlotSpecCompareDialog, self)._finalize()

    def __serverSettingsChange(self, *_):
        if not self.__vehicleComparisonBasket.isEnabled() or not self.__vehicle.isRoleSlotExists():
            self._onCancel()


@wg_async
def showDialog(vehicle, parent=None):
    result = yield wg_await(showSingleDialogWithResultData(layoutID=R.views.lobby.vehicle_compare.SelectSlotSpecCompareDialog(), parent=parent, wrappedViewClass=SelectSlotSpecCompareDialog, vehicle=vehicle))
    raise AsyncReturn(result)
