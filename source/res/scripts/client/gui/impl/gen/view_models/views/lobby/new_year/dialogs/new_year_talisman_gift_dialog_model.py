# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/new_year_talisman_gift_dialog_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class NewYearTalismanGiftDialogModel(ViewModel):
    __slots__ = ('onShowCongratButtons',)

    def __init__(self, properties=8, commands=1):
        super(NewYearTalismanGiftDialogModel, self).__init__(properties=properties, commands=commands)

    def getDialogType(self):
        return self._getString(0)

    def setDialogType(self, value):
        self._setString(0, value)

    def getTalismanType(self):
        return self._getString(1)

    def setTalismanType(self, value):
        self._setString(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    def getContentWidthSmall(self):
        return self._getNumber(3)

    def setContentWidthSmall(self, value):
        self._setNumber(3, value)

    def getContentWidthMedium(self):
        return self._getNumber(4)

    def setContentWidthMedium(self, value):
        self._setNumber(4, value)

    def getContentWidthLarge(self):
        return self._getNumber(5)

    def setContentWidthLarge(self, value):
        self._setNumber(5, value)

    def getHorizontalChangeBreakpointSM(self):
        return self._getNumber(6)

    def setHorizontalChangeBreakpointSM(self, value):
        self._setNumber(6, value)

    def getHorizontalChangeBreakpointML(self):
        return self._getNumber(7)

    def setHorizontalChangeBreakpointML(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(NewYearTalismanGiftDialogModel, self)._initialize()
        self._addStringProperty('dialogType', '')
        self._addStringProperty('talismanType', '')
        self._addArrayProperty('rewards', Array())
        self._addNumberProperty('contentWidthSmall', -1)
        self._addNumberProperty('contentWidthMedium', -1)
        self._addNumberProperty('contentWidthLarge', -1)
        self._addNumberProperty('horizontalChangeBreakpointSM', 0)
        self._addNumberProperty('horizontalChangeBreakpointML', 0)
        self.onShowCongratButtons = self._addCommand('onShowCongratButtons')
