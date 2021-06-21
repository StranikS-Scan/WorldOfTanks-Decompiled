# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_post_progression/dialogs/destroy_pair_modification.py
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.common.format_resource_string_arg_model import FormatResourceStringArgModel
from gui.impl.gen.view_models.views.lobby.demount_kit.item_price_dialog_model import ItemPriceDialogModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import DIALOG_TYPES, FullScreenDialogView
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from gui.veh_post_porgression.models.ext_money import EXT_MONEY_ZERO
from uilogging.veh_post_progression.constants import LogAdditionalInfo
from uilogging.veh_post_progression.loggers import VehPostProgressionDialogLogger

class DestroyPairModificationsDialog(FullScreenDialogView[ItemPriceDialogModel]):
    __slots__ = ('__vehicle', '__stepIDs')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.demountkit.CommonWindow(), model=ItemPriceDialogModel())
        settings.args = args
        settings.kwargs = kwargs
        self.__vehicle = kwargs.get('vehicle', None)
        self.__stepIDs = kwargs.get('stepIDs', ())
        super(DestroyPairModificationsDialog, self).__init__(settings)
        return

    def _onInventoryResync(self, reason, diff):
        super(DestroyPairModificationsDialog, self)._onInventoryResync(reason, diff)
        changedVehicles = diff.get(GUI_ITEM_TYPE.VEHICLE, {})
        if self.__vehicle.intCD in changedVehicles:
            self.__vehicle = self._itemsCache.items.getItemByCD(self.__vehicle.intCD)
        if self.__checkDestroyPossible():
            with self.viewModel.transaction() as model:
                self.__updatePrice(model)
        else:
            self._onCancel()

    def _onLoading(self, *args, **kwargs):
        super(DestroyPairModificationsDialog, self)._onLoading(*args, **kwargs)
        rPath = R.strings.veh_post_progression.destroyPairModificationsDialog
        with self.viewModel.transaction() as model:
            self.__updatePrice(model)
            model.setDialogType(DIALOG_TYPES.WARNING)
            if len(self.__stepIDs) > 1:
                model.setTitleBody(rPath.destroyAll.title())
                model.setDescription(rPath.destroyAll.description())
            elif self.__stepIDs:
                model.setTitleBody(rPath.destroyOne.title())
                model.setDescription(rPath.destroyOne.description())
                action = self.__vehicle.postProgression.getStep(self.__stepIDs[0]).action
                self.__setModificationName(model.getTitleArgs(), action.modifications[action.getPurchasedIdx()])
            model.setAcceptButtonText(rPath.acceptButton())
            model.setCancelButtonText(rPath.cancelButton())
            model.setShowPriceWarning(True)

    def _onCancelClicked(self):
        super(DestroyPairModificationsDialog, self)._onCancelClicked()
        VehPostProgressionDialogLogger().logClick(LogAdditionalInfo.DESTROY_MODIFICATION)

    def __updatePrice(self, model=None):
        if model is None:
            model = self.viewModel
        if self.__stepIDs:
            action = self.__vehicle.postProgression.getStep(self.__stepIDs[0]).action
            price = action.modifications[action.getPurchasedIdx()].getPrice()
        else:
            price = EXT_MONEY_ZERO
        model.setItemPrice(price.credits)
        model.setCurrencyType(Currency.CREDITS)
        return

    def __setModificationName(self, arrModel, modification):
        frmtModel = FormatResourceStringArgModel()
        frmtModel.setName('modification')
        frmtModel.setValue(backport.text(modification.getLocNameRes()()))
        arrModel.addViewModel(frmtModel)
        arrModel.invalidate()

    def __checkDestroyPossible(self):
        self.__vehicle = self._itemsCache.items.getItemByCD(self.__vehicle.intCD)
        if self.__vehicle is not None and self.__vehicle.postProgressionAvailability:
            for stepID in self.__stepIDs:
                step = self.__vehicle.postProgression.getStep(stepID)
                if not step.action.mayDiscardInner():
                    return False

            return True
        else:
            return False
