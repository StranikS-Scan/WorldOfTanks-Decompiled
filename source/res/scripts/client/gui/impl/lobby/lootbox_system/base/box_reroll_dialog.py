# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/base/box_reroll_dialog.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootbox_system.confirmation_model import ConfirmationModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons

class BoxRerollView(FullScreenDialogBaseView):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.mono.lootbox.dialogs.reroll_dialog())
        settings.model = ConfirmationModel()
        settings.args = args
        settings.kwargs = kwargs
        super(BoxRerollView, self).__init__(settings)
        self.__additionalData = {}

    @property
    def viewModel(self):
        return super(BoxRerollView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.confirm, self.__confirm), (self.viewModel.cancel, self.__cancel))

    def _onLoading(self, *args, **kwargs):
        super(BoxRerollView, self)._onLoading(*args, **kwargs)
        with self.viewModel as model:
            model.setEventName(kwargs.get('eventName', ''))
            model.price.setName(kwargs.get('currency', ''))
            model.price.setValue(kwargs.get('price', 0))

    def _getAdditionalData(self):
        return self.__additionalData

    def __confirm(self):
        self._setResult(DialogButtons.SUBMIT)

    def __cancel(self):
        self.__additionalData['isUserCancelAction'] = True
        self._setResult(DialogButtons.CANCEL)
