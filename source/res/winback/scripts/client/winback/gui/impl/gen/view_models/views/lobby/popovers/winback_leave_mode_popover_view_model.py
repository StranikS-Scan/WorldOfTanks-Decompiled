# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/gen/view_models/views/lobby/popovers/winback_leave_mode_popover_view_model.py
from frameworks.wulf import ViewModel

class WinbackLeaveModePopoverViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=1, commands=1):
        super(WinbackLeaveModePopoverViewModel, self).__init__(properties=properties, commands=commands)

    def getBattlesCount(self):
        return self._getNumber(0)

    def setBattlesCount(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(WinbackLeaveModePopoverViewModel, self)._initialize()
        self._addNumberProperty('battlesCount', 0)
        self.onClick = self._addCommand('onClick')
