# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/dismiss_tankman_dialog.py
from base_crew_dialog_template_view import BaseCrewDialogTemplateView
from gui.impl.dialogs.dialog_template_button import CancelButton, ConfirmButton
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.dialogs.dismiss_tankman_dialog_model import DismissTankmanDialogModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.crew.crew_helpers.model_setters import setTankmanModel, setReplacedTankmanModel, setTmanSkillsModel
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared.gui_items.Tankman import Tankman, MAX_ROLE_LEVEL
from gui.shared.gui_items.items_actions import factory
from helpers import dependency, time_utils
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.shared import IItemsCache
from uilogging.crew.logging_constants import CrewDialogKeys

class DismissTankmanDialog(BaseCrewDialogTemplateView):
    __slots__ = ('_tankman',)
    LAYOUT_ID = R.views.lobby.crew.dialogs.DismissTankmanDialog()
    VIEW_MODEL = DismissTankmanDialogModel
    _itemsCache = dependency.descriptor(IItemsCache)
    _restoreCtrl = dependency.descriptor(IRestoreController)

    def __init__(self, tankmanId, **kwargs):
        super(DismissTankmanDialog, self).__init__(loggingKey=CrewDialogKeys.DISMISS_TANKMAN, **kwargs)
        self._tankman = self._itemsCache.items.getTankman(tankmanId)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onInputChanged, self._onInputChanged),)

    def _onLoading(self, *args, **kwargs):
        self.setBackgroundImagePath(R.images.gui.maps.icons.windows.background())
        self.addButton(ConfirmButton(R.strings.dialogs.dismissTankman.buttons.dismiss(), isDisabled=True))
        self.addButton(CancelButton())
        self._updateViewModel()
        super(DismissTankmanDialog, self)._onLoading(*args, **kwargs)

    @args2params(str)
    def _onInputChanged(self, value):
        descriptor = self._tankman.descriptor
        controlNumber = descriptor.lastSkillLevel if self._tankman.skills else descriptor.roleLevel
        self.getButton(DialogButtons.SUBMIT).isDisabled = value != str(controlNumber)
        self.setFocusedIndex(0 if value == str(controlNumber) else -1)

    def _setResult(self, result):
        if result == DialogButtons.SUBMIT:
            factory.doAction(factory.DISMISS_TANKMAN, self._tankman.invID)
        super(DismissTankmanDialog, self)._setResult(result)

    def _updateViewModel(self):
        with self.viewModel.transaction() as vm:
            self._fillViewModel(vm)

    def _fillViewModel(self, vm):
        tmanNativeVeh = self._itemsCache.items.getItemByCD(self._tankman.vehicleNativeDescr.type.compactDescr)
        setTankmanModel(vm.tankman, self._tankman, tmanNativeVeh)
        vm.setIsRecoveryPossible(self._tankman.isRestorable())
        setTmanSkillsModel(vm.tankman.getSkills(), self._tankman)
        if self._tankman.skills:
            vm.setPerkName(self._tankman.descriptor.skills[-1])
            vm.setPerkLevel(self._tankman.descriptor.lastSkillLevel)
        if self._tankman.isRestorable():
            tankmenRestoreConfig = self._itemsCache.items.shop.tankmenRestoreConfig
            restoreDays = tankmenRestoreConfig.billableDuration / time_utils.ONE_DAY
            dismissedTmenList = self._restoreCtrl.getDismissedTankmen()
            dismissedTmenSize = len(dismissedTmenList)
            vm.setDismissPeriod(restoreDays)
            isLmtReached = self._restoreCtrl.getMaxTankmenBufferLength() - dismissedTmenSize <= 0
            vm.setIsLimitReached(isLmtReached)
            if isLmtReached and dismissedTmenSize:
                replacedTman = dismissedTmenList[-1]
                replacedTmanVeh = self._itemsCache.items.getItemByCD(replacedTman.vehicleNativeDescr.type.compactDescr)
                setReplacedTankmanModel(vm.replacedTankman, replacedTman, replacedTmanVeh)
        vm.setTrainingLevel(self._tankman.roleLevel)
        self.getButton(DialogButtons.SUBMIT).isDisabled = self._tankman.roleLevel == MAX_ROLE_LEVEL
