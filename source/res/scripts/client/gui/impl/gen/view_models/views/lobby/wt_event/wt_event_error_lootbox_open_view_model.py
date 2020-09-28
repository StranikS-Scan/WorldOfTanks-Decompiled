# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_error_lootbox_open_view_model.py
from frameworks.wulf import ViewModel

class WtEventErrorLootboxOpenViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(WtEventErrorLootboxOpenViewModel, self).__init__(properties=properties, commands=commands)

    def getErrorTitle(self):
        return self._getString(0)

    def setErrorTitle(self, value):
        self._setString(0, value)

    def getErrorText(self):
        return self._getString(1)

    def setErrorText(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(WtEventErrorLootboxOpenViewModel, self)._initialize()
        self._addStringProperty('errorTitle', '')
        self._addStringProperty('errorText', '')
        self.onClose = self._addCommand('onClose')
