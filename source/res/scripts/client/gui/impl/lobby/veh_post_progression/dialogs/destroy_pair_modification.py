# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_post_progression/dialogs/destroy_pair_modification.py
from gui.impl import backport
from gui.impl.dialogs.dialog_template import DialogTemplateView
from gui.impl.dialogs.dialog_template_button import ConfirmButton, CancelButton
from gui.impl.dialogs.sub_views.content.simple_text_content import SimpleTextContent
from gui.impl.dialogs.sub_views.icon.icon_set import IconSet
from gui.impl.dialogs.sub_views.title.simple_text_title import SimpleTextTitle
from gui.impl.dialogs.sub_views.top_right.money_balance import MoneyBalance
from gui.impl.gen.view_models.views.dialogs.default_dialog_place_holders import DefaultDialogPlaceHolders
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from shared_utils import first
_R_PATH = R.strings.veh_post_progression.destroyPairModificationsDialog

class DestroyPairModificationsDialog(DialogTemplateView):
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__vehicle', '__stepIDs')

    def __init__(self, layoutID=None, uniqueID=None, *args, **kwargs):
        super(DestroyPairModificationsDialog, self).__init__(layoutID, uniqueID, *args, **kwargs)
        self.__vehicle = kwargs.get('vehicle', None)
        self.__stepIDs = kwargs.get('stepIDs', ())
        return

    def _initialize(self, *args, **kwargs):
        super(DestroyPairModificationsDialog, self)._initialize()
        self.__itemsCache.onSyncCompleted += self.__onInventoryResync

    def _finalize(self):
        self.__itemsCache.onSyncCompleted -= self.__onInventoryResync
        super(DestroyPairModificationsDialog, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        if self.__checkDestroy():
            self._setResult(DialogButtons.CANCEL)
            return
        self.setSubView(DefaultDialogPlaceHolders.TOP_RIGHT, MoneyBalance())
        self.setSubView(DefaultDialogPlaceHolders.TITLE, SimpleTextTitle(self.__getTitleText()))
        self.setSubView(DefaultDialogPlaceHolders.CONTENT, SimpleTextContent(self.__getDescriptionText()))
        self.setSubView(DefaultDialogPlaceHolders.ICON, IconSet(R.images.gui.maps.uiKit.dialogs.icons.alert(), [R.images.gui.maps.uiKit.dialogs.highlights.red_1()]))
        self.addButton(ConfirmButton(label=_R_PATH.acceptButton()))
        self.addButton(CancelButton(label=_R_PATH.cancelButton()))
        super(DestroyPairModificationsDialog, self)._onLoading(*args, **kwargs)

    def __getTitleText(self):
        if len(self.__stepIDs) == 1:
            mod = self.__vehicle.postProgression.getStep(self.__stepIDs[0]).action.getPurchasedModification()
            return backport.text(_R_PATH.destroyOne.title(), modification=backport.text(mod.getLocNameRes()()))
        return _R_PATH.destroyAll.title()

    def __getDescriptionText(self):
        action = self.__vehicle.postProgression.getStep(self.__stepIDs[0]).action
        currency, _ = first(action.getPurchasedModification().getPrice().iteritems())
        return _R_PATH.destroyOne.description.dyn(currency, _R_PATH.destroyOne.description.default) if len(self.__stepIDs) == 1 else _R_PATH.destroyAll.description.dyn(currency, _R_PATH.destroyAll.description.default)

    def __onInventoryResync(self, _, diff):
        changedVehicles = diff.get(GUI_ITEM_TYPE.VEHICLE, {})
        if self.__vehicle.intCD in changedVehicles:
            self.__vehicle = self.__itemsCache.items.getItemByCD(self.__vehicle.intCD)
        if self.__checkDestroy():
            self._setResult(DialogButtons.CANCEL)
        else:
            self.__updatePrice(self.getSubView(DefaultDialogPlaceHolders.CONTENT))

    def __updatePrice(self, contentModel):
        if contentModel is None:
            return
        else:
            contentModel.updateText(self.__getDescriptionText())
            return

    def __checkDestroy(self):
        if self.__vehicle is None:
            return True
        elif not self.__stepIDs:
            return True
        else:
            self.__vehicle = self.__itemsCache.items.getItemByCD(self.__vehicle.intCD)
            if not self.__vehicle.postProgressionAvailability():
                return True
            for stepID in self.__stepIDs:
                step = self.__vehicle.postProgression.getStep(stepID)
                if not step.action.isMultiAction() or not step.action.mayDiscardInner():
                    return True

            return False
