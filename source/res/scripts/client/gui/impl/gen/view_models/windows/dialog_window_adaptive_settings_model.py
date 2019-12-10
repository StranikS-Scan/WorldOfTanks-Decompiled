# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/windows/dialog_window_adaptive_settings_model.py
from frameworks.wulf import ViewModel

class DialogWindowAdaptiveSettingsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(DialogWindowAdaptiveSettingsModel, self).__init__(properties=properties, commands=commands)

    def getContentHorizontalAlign(self):
        return self._getNumber(0)

    def setContentHorizontalAlign(self, value):
        self._setNumber(0, value)

    def getButtonsHorizontalAlign(self):
        return self._getNumber(1)

    def setButtonsHorizontalAlign(self, value):
        self._setNumber(1, value)

    def getHorizontalChangeBreakpointSM(self):
        return self._getNumber(2)

    def setHorizontalChangeBreakpointSM(self, value):
        self._setNumber(2, value)

    def getHorizontalChangeBreakpointML(self):
        return self._getNumber(3)

    def setHorizontalChangeBreakpointML(self, value):
        self._setNumber(3, value)

    def getContentHorizontalOffsetSmall(self):
        return self._getNumber(4)

    def setContentHorizontalOffsetSmall(self, value):
        self._setNumber(4, value)

    def getContentHorizontalOffsetMedium(self):
        return self._getNumber(5)

    def setContentHorizontalOffsetMedium(self, value):
        self._setNumber(5, value)

    def getContentHorizontalOffsetLarge(self):
        return self._getNumber(6)

    def setContentHorizontalOffsetLarge(self, value):
        self._setNumber(6, value)

    def getContentWidthSmall(self):
        return self._getNumber(7)

    def setContentWidthSmall(self, value):
        self._setNumber(7, value)

    def getContentWidthMedium(self):
        return self._getNumber(8)

    def setContentWidthMedium(self, value):
        self._setNumber(8, value)

    def getContentWidthLarge(self):
        return self._getNumber(9)

    def setContentWidthLarge(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(DialogWindowAdaptiveSettingsModel, self)._initialize()
        self._addNumberProperty('contentHorizontalAlign', 4)
        self._addNumberProperty('buttonsHorizontalAlign', 4)
        self._addNumberProperty('horizontalChangeBreakpointSM', 0)
        self._addNumberProperty('horizontalChangeBreakpointML', 0)
        self._addNumberProperty('contentHorizontalOffsetSmall', 0)
        self._addNumberProperty('contentHorizontalOffsetMedium', 0)
        self._addNumberProperty('contentHorizontalOffsetLarge', 0)
        self._addNumberProperty('contentWidthSmall', 0)
        self._addNumberProperty('contentWidthMedium', 0)
        self._addNumberProperty('contentWidthLarge', 0)
