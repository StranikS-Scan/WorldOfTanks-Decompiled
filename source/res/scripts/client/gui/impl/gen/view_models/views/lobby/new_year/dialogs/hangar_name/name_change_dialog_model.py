# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/hangar_name/name_change_dialog_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_hangar_name_model import NyHangarNameModel

class NameChangeDialogModel(ViewModel):
    __slots__ = ('onAccept', 'onCancel')

    def __init__(self, properties=1, commands=2):
        super(NameChangeDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def hangarName(self):
        return self._getViewModel(0)

    @staticmethod
    def getHangarNameType():
        return NyHangarNameModel

    def _initialize(self):
        super(NameChangeDialogModel, self)._initialize()
        self._addViewModelProperty('hangarName', NyHangarNameModel())
        self.onAccept = self._addCommand('onAccept')
        self.onCancel = self._addCommand('onCancel')
