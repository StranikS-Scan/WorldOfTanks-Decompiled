# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bm2021/dialogs/black_market_exit_confirm_dialog.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.bm2021.dialogs.black_market_exit_confirm_dialog_model import BlackMarketExitConfirmDialogModel
from gui.impl.lobby.bm2021.sound import BLACK_MARKET_OVERLAY_SOUND_SPACE
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView

class BlackMarketExitConfirmDialog(FullScreenDialogView):
    __slots__ = ('__endDate',)
    _COMMON_SOUND_SPACE = BLACK_MARKET_OVERLAY_SOUND_SPACE

    def __init__(self, endDate):
        settings = ViewSettings(R.views.lobby.bm2021.dialogs.ConfirmExit())
        settings.model = BlackMarketExitConfirmDialogModel()
        super(BlackMarketExitConfirmDialog, self).__init__(settings)
        self.__endDate = endDate

    @property
    def viewModel(self):
        return super(BlackMarketExitConfirmDialog, self).getViewModel()

    def _setBaseParams(self, model):
        model.setEndDate(self.__endDate)

    def _addListeners(self):
        self.viewModel.onConfirm += self._onAccept

    def _removeListeners(self):
        self.viewModel.onConfirm -= self._onAccept
