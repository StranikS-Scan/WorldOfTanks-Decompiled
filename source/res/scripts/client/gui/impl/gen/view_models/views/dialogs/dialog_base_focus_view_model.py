# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/dialog_base_focus_view_model.py
from frameworks.wulf import ViewModel

class DialogBaseFocusViewModel(ViewModel):
    __slots__ = ('onGotFocus',)

    def __init__(self, properties=1, commands=1):
        super(DialogBaseFocusViewModel, self).__init__(properties=properties, commands=commands)

    def getFocusedIndex(self):
        return self._getNumber(0)

    def setFocusedIndex(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(DialogBaseFocusViewModel, self)._initialize()
        self._addNumberProperty('focusedIndex', -1)
        self.onGotFocus = self._addCommand('onGotFocus')
