# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/base_view.py
from PlayerEvents import g_playerEvents
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_completion.common.base_dialog_model import BaseDialogModel
from gui.impl.pub import ViewImpl

class BaseView(ViewImpl):
    _TITLE = R.invalid()
    _SUBTITLE = R.invalid()

    @property
    def viewModel(self):
        return super(BaseView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BaseView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self._fillModel(model)

    def _initialize(self, *args, **kwargs):
        super(BaseView, self)._initialize(*args, **kwargs)
        self._addListeners()

    def _finalize(self):
        super(BaseView, self)._finalize()
        self._removeListeners()

    def _addListeners(self):
        self.viewModel.onAcceptClicked += self._onAccept
        self.viewModel.onCancelClicked += self._onCancel
        g_playerEvents.onAccountBecomeNonPlayer += self._onAccountBecomeNonPlayer

    def _removeListeners(self):
        self.viewModel.onAcceptClicked -= self._onAccept
        self.viewModel.onCancelClicked -= self._onCancel
        g_playerEvents.onAccountBecomeNonPlayer -= self._onAccountBecomeNonPlayer

    def _fillModel(self, model):
        model.setTitle(self._TITLE)
        model.setSubTitle(self._SUBTITLE)

    def _updateModel(self, *args, **kwargs):
        pass

    def _onAccept(self, *args):
        self.destroyWindow()

    def _onCancel(self):
        self.destroyWindow()

    def _onAccountBecomeNonPlayer(self):
        self.destroyWindow()
