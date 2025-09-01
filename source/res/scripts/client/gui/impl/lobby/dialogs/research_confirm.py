# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/research_confirm.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.dialogs.research_confirm_dialog_view_model import ResearchConfirmDialogViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class ResearchConfirmDialogWindow(FullScreenDialogBaseView):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.mono.dialogs.research_confirm_dialog(), model=ResearchConfirmDialogViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(ResearchConfirmDialogWindow, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ResearchConfirmDialogWindow, self).getViewModel()

    def _onLoading(self, researchedItemsText, xp, freeXP, *args, **kwargs):
        super(ResearchConfirmDialogWindow, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            vm.setResearchedItemsText(researchedItemsText)
            vm.setXp(xp)
            vm.setFreeXP(freeXP)

    def _getEvents(self):
        events = super(ResearchConfirmDialogWindow, self)._getEvents()
        return events + ((self.viewModel.onAcceptClick, self._onAcceptClick), (self.viewModel.onCancelClick, self._onCancelClick))

    def _onAcceptClick(self):
        self._setResult(DialogButtons.SUBMIT)

    def _onCancelClick(self):
        self._setResult(DialogButtons.CANCEL)
