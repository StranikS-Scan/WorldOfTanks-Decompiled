# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/dialogs/hangar_name/name_change_dialog.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.hangar_name.name_change_dialog_model import NameChangeDialogModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons

class NameChangeDialog(FullScreenDialogBaseView):
    __slots__ = ('__titleId', '__descriptionId')

    def __init__(self, nameID, descID):
        settings = ViewSettings(R.views.lobby.new_year.dialogs.hangar_name.NameChangeDialog())
        settings.model = NameChangeDialogModel()
        self.__titleId = nameID
        self.__descriptionId = descID
        super(NameChangeDialog, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NameChangeDialog, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onAccept, self.__onAccept), (self.viewModel.onCancel, self.__onCancel))

    def _onLoading(self, *args, **kwargs):
        super(NameChangeDialog, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.hangarName.setTitle(self.__titleId)
            tx.hangarName.setDescription(self.__descriptionId)

    def __onAccept(self):
        self._setResult(DialogButtons.SUBMIT)

    def __onCancel(self):
        self._setResult(DialogButtons.CANCEL)
