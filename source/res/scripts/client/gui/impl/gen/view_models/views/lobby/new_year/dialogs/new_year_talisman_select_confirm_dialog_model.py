# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/new_year_talisman_select_confirm_dialog_model.py
from frameworks.wulf import ViewModel

class NewYearTalismanSelectConfirmDialogModel(ViewModel):
    __slots__ = ('onSelectClick', 'onCloseBtnClick')

    def __init__(self, properties=6, commands=2):
        super(NewYearTalismanSelectConfirmDialogModel, self).__init__(properties=properties, commands=commands)

    def getTalismanType(self):
        return self._getString(0)

    def setTalismanType(self, value):
        self._setString(0, value)

    def getContentWidthSmall(self):
        return self._getNumber(1)

    def setContentWidthSmall(self, value):
        self._setNumber(1, value)

    def getContentWidthMedium(self):
        return self._getNumber(2)

    def setContentWidthMedium(self, value):
        self._setNumber(2, value)

    def getContentWidthLarge(self):
        return self._getNumber(3)

    def setContentWidthLarge(self, value):
        self._setNumber(3, value)

    def getHorizontalChangeBreakpointSM(self):
        return self._getNumber(4)

    def setHorizontalChangeBreakpointSM(self, value):
        self._setNumber(4, value)

    def getHorizontalChangeBreakpointML(self):
        return self._getNumber(5)

    def setHorizontalChangeBreakpointML(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(NewYearTalismanSelectConfirmDialogModel, self)._initialize()
        self._addStringProperty('talismanType', '')
        self._addNumberProperty('contentWidthSmall', -1)
        self._addNumberProperty('contentWidthMedium', -1)
        self._addNumberProperty('contentWidthLarge', -1)
        self._addNumberProperty('horizontalChangeBreakpointSM', 0)
        self._addNumberProperty('horizontalChangeBreakpointML', 0)
        self.onSelectClick = self._addCommand('onSelectClick')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
