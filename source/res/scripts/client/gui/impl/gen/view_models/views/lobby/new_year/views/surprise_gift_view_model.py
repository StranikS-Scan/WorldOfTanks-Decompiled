# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/surprise_gift_view_model.py
from frameworks.wulf import ViewModel

class SurpriseGiftViewModel(ViewModel):
    __slots__ = ('onClaim', 'closeWindow')

    def __init__(self, properties=1, commands=2):
        super(SurpriseGiftViewModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getString(0)

    def setDescription(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(SurpriseGiftViewModel, self)._initialize()
        self._addStringProperty('description', '')
        self.onClaim = self._addCommand('onClaim')
        self.closeWindow = self._addCommand('closeWindow')
