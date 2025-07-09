# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/dismiss_selected_tankmans.py
from gui.impl.gen.view_models.views.lobby.crew.dialogs.dismiss_or_restore_dialog_model import DismissOrRestoreDialogModel, DialogType
from gui.impl.gen import R
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from uilogging.crew.logging_constants import CrewDialogKeys
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.gui_decorators import args2params
from gui.impl.pub.dialog_window import DialogButtons
from helpers import dependency
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.shared import IItemsCache
from gui.shared.gui_items.items_actions import factory

class DismissSelectedTankmans(BaseCrewDialogTemplateView):
    __slots__ = ('__tankmans', '__restorableCount', '_restoreLimit', '__limitOverCount')
    LAYOUT_ID = R.views.lobby.crew.dialogs.DismissOrRestoreTankmans()
    VIEW_MODEL = DismissOrRestoreDialogModel
    DIALOG_TYPE = DialogType.DISMISS
    _itemsCache = dependency.descriptor(IItemsCache)
    _restoreCtrl = dependency.descriptor(IRestoreController)

    def __init__(self, tankmans, **kwargs):
        super(DismissSelectedTankmans, self).__init__(loggingKey=CrewDialogKeys.DISMISS_OR_RESTORE, **kwargs)
        self.__tankmans = self._setTankmans(tankmans)
        self.__restorableCount = self._setRestorableTankmans()
        self._restoreLimit = self._itemsCache.items.shop.tankmenRestoreConfig.limit
        self.__limitOverCount = 0

    @property
    def viewModel(self):
        return super(DismissSelectedTankmans, self).getViewModel()

    def _setTankmans(self, tankmanIDs):
        return [ t for t in (self._itemsCache.items.getTankman(ID) for ID in tankmanIDs) if t ]

    def _setRestorableTankmans(self):
        return sum((1 for t in self.__tankmans if t.isRestorable()))

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        self.addButton(ConfirmButton(label=R.strings.dialogs.dismissTankman.buttons.dyn(self.DIALOG_TYPE.value)(), isDisabled=True))
        self.addButton(CancelButton())
        self._checkIsLimitOver()
        self._updateViewModel()
        super(DismissSelectedTankmans, self)._onLoading(*args, **kwargs)

    def _getEvents(self):
        return [(self.viewModel.onChangeCaptcha, self.__onChangeCaptcha)]

    def _checkIsLimitOver(self):
        totalDismissedCount = len(self._restoreCtrl.getDismissedTankmen()) + self.__restorableCount
        self.__limitOverCount = max(0, totalDismissedCount - self._restoreLimit)

    def _updateViewModel(self):
        with self.viewModel.transaction() as vm:
            self._fillViewModel(vm)

    def _fillViewModel(self, vm):
        vm.setLimitOverCount(self.__limitOverCount)
        vm.setTankmans(len(self.__tankmans))
        vm.setTankmansWithPerk(self.__restorableCount)
        vm.setDialogType(self.DIALOG_TYPE)

    @args2params(bool)
    def __onChangeCaptcha(self, value):
        confirmBtn = self.getButton(DialogButtons.SUBMIT)
        if confirmBtn is not None:
            confirmBtn.isDisabled = value
        with self.viewModel.transaction() as vm:
            vm.setDisabled(value)
        return

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            factory.doAction(factory.DISMISS_TANKMAN, self.__tankmans)
        super(DismissSelectedTankmans, self)._setResult(result)
