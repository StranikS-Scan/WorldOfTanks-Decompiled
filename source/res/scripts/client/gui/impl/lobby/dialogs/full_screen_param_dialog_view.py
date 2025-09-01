# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/dialogs/full_screen_param_dialog_view.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.dialogs.dialog_template_param_view_model import DialogTemplateParamViewModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons
_logger = logging.getLogger(__name__)

class FullScreenParamDialogView(FullScreenDialogBaseView):
    __slots__ = ('__additionalData', '__type', '__params')
    VIEW_MODEL = DialogTemplateParamViewModel

    def __init__(self, *args, **kwargs):
        layoutID = kwargs.pop('dialogLayoutID', None)
        self.__type = kwargs.pop('dialogType', None)
        self.__params = kwargs.pop('dialogParams', None)
        self.__additionalData = None
        settings = ViewSettings(layoutID)
        settings.model = self.VIEW_MODEL()
        settings.args = args
        settings.kwargs = kwargs
        super(FullScreenParamDialogView, self).__init__(settings, *args, **kwargs)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.viewModel.onAction += self._actionHandler
        self.viewModel.onClose += self._closeHandler
        with self.viewModel.transaction() as model:
            model.setType(self.__type)
            model.setParams(self.__params)
        super(FullScreenParamDialogView, self)._onLoading(*args, **kwargs)

    def _finalize(self):
        self.viewModel.onAction -= self._actionHandler
        self.viewModel.onClose -= self._closeHandler
        self.__additionalData = None
        super(FullScreenParamDialogView, self)._finalize()
        return

    def _getAdditionalData(self):
        return self.__additionalData

    def _actionHandler(self, args):
        self.__additionalData = args
        actionID = args.get('action')
        if not actionID:
            _logger.warning('Empty action has been received...')
        self._setResult(DialogButtons.SUBMIT)

    def _closeHandler(self, _=None):
        self._setResult(DialogButtons.CANCEL)
