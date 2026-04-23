# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/dialogs/abilities_inclomplete_dialog_model.py
from frameworks.wulf import ViewModel

class AbilitiesInclompleteDialogModel(ViewModel):
    __slots__ = ('onSubmitClick', 'onCancelClick', 'onCloseClick')

    def __init__(self, properties=0, commands=3):
        super(AbilitiesInclompleteDialogModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(AbilitiesInclompleteDialogModel, self)._initialize()
        self.onSubmitClick = self._addCommand('onSubmitClick')
        self.onCancelClick = self._addCommand('onCancelClick')
        self.onCloseClick = self._addCommand('onCloseClick')
