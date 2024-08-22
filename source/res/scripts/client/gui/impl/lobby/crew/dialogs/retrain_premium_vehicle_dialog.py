# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/retrain_premium_vehicle_dialog.py
from typing import TYPE_CHECKING
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen.view_models.views.lobby.crew.dialogs.retrain_premium_vehicle_dialog_model import RetrainPremiumVehicleDialogModel
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class RetrainPremiumVehicleDialog(BaseCrewDialogTemplateView):
    __slots__ = ('_vehicle', '_isMassive')
    LAYOUT_ID = R.views.lobby.crew.dialogs.RetrainPremiumVehicleDialog()
    VIEW_MODEL = RetrainPremiumVehicleDialogModel
    _itemsCache = dependency.descriptor(IItemsCache)
    _appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, vehicleCD, isMassive, **kwargs):
        self._vehicle = self._itemsCache.items.getItemByCD(vehicleCD)
        self._isMassive = isMassive
        super(RetrainPremiumVehicleDialog, self).__init__(**kwargs)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        self.setSubView(DefaultDialogPlaceHolders.TOP_RIGHT, MoneyBalance())
        self.setSubView(DefaultDialogPlaceHolders.ICON, IconSet(R.images.gui.maps.uiKit.dialogs.icons.alert(), [R.images.gui.maps.uiKit.dialogs.highlights.red_1()]))
        self.addButton(ConfirmButton(R.strings.dialogs.common.submit()))
        self.addButton(CancelButton(R.strings.dialogs.retrain.cancel()))
        self._initModel()
        super(RetrainPremiumVehicleDialog, self)._onLoading(*args, **kwargs)

    def _initModel(self):
        with self.viewModel.transaction() as vm:
            vm.setIsMassRetrain(self._isMassive)
            fillVehicleInfo(vm.vehicle, self._vehicle, tags=[VEHICLE_TAGS.PREMIUM])
