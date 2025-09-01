# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/dialogs/research_confirm_dialog_view_model.py
from frameworks.wulf import ViewModel

class ResearchConfirmDialogViewModel(ViewModel):
    __slots__ = ('onAcceptClick', 'onCancelClick')

    def __init__(self, properties=3, commands=2):
        super(ResearchConfirmDialogViewModel, self).__init__(properties=properties, commands=commands)

    def getXp(self):
        return self._getNumber(0)

    def setXp(self, value):
        self._setNumber(0, value)

    def getFreeXP(self):
        return self._getNumber(1)

    def setFreeXP(self, value):
        self._setNumber(1, value)

    def getResearchedItemsText(self):
        return self._getString(2)

    def setResearchedItemsText(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(ResearchConfirmDialogViewModel, self)._initialize()
        self._addNumberProperty('xp', 0)
        self._addNumberProperty('freeXP', 0)
        self._addStringProperty('researchedItemsText', '')
        self.onAcceptClick = self._addCommand('onAcceptClick')
        self.onCancelClick = self._addCommand('onCancelClick')
