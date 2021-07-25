# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/dialogs/apply_exp_exchange_dialog_view.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.dialogs.apply_exp_exchange_dialog_view_model import ApplyExpExchangeDialogViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogView
from uilogging.detachment.loggers import DetachmentLogger
from uilogging.detachment.constants import GROUP, ACTION
_logger = logging.getLogger(__name__)

class ApplyExpExchangeDialogView(FullScreenDialogView):
    __slots__ = ('_freeXP', '_detachmentXPRate', '_isMaxLevel')
    uiLogger = DetachmentLogger(GROUP.XP_EXCHANGE_CONFIRM_DIALOG)

    def __init__(self, freeXP, detachmentXPRate, isMaxLevel=False):
        settings = ViewSettings(R.views.lobby.detachment.dialogs.ApplyExpExchangeDialogView())
        settings.model = ApplyExpExchangeDialogViewModel()
        self._freeXP = freeXP
        self._detachmentXPRate = detachmentXPRate
        self._isMaxLevel = isMaxLevel
        super(ApplyExpExchangeDialogView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ApplyExpExchangeDialogView, self).getViewModel()

    def _setBaseParams(self, model):
        with model.transaction() as viewModel:
            viewModel.setFreeExp(self._freeXP)
            viewModel.setRate(self._detachmentXPRate)
            viewModel.setIsMaxLevel(self._isMaxLevel)
            viewModel.setTitleBody(R.strings.dialogs.detachment.applyExpExchange.title())
            viewModel.setAcceptButtonText(R.strings.detachment.common.convert())
            viewModel.setCancelButtonText(R.strings.detachment.common.cancel())
        super(ApplyExpExchangeDialogView, self)._setBaseParams(model)

    def _onAcceptClicked(self):
        self.uiLogger.log(ACTION.DIALOG_CONFIRM)
        super(ApplyExpExchangeDialogView, self)._onAcceptClicked()

    def _onCancelClicked(self):
        self.uiLogger.log(ACTION.DIALOG_CANCEL)
        super(ApplyExpExchangeDialogView, self)._onCancelClicked()

    def _onExitClicked(self):
        self.uiLogger.log(ACTION.DIALOG_EXIT)
        super(ApplyExpExchangeDialogView, self)._onExitClicked()
