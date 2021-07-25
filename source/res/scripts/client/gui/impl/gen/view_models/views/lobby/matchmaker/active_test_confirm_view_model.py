# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/matchmaker/active_test_confirm_view_model.py
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class ActiveTestConfirmViewModel(FullScreenDialogWindowModel):
    __slots__ = ('onOpenPortalClicked',)

    def __init__(self, properties=13, commands=4):
        super(ActiveTestConfirmViewModel, self).__init__(properties=properties, commands=commands)

    def getClusterName(self):
        return self._getString(10)

    def setClusterName(self, value):
        self._setString(10, value)

    def getTimeRangeStart(self):
        return self._getNumber(11)

    def setTimeRangeStart(self, value):
        self._setNumber(11, value)

    def getTimeRangeEnd(self):
        return self._getNumber(12)

    def setTimeRangeEnd(self, value):
        self._setNumber(12, value)

    def _initialize(self):
        super(ActiveTestConfirmViewModel, self)._initialize()
        self._addStringProperty('clusterName', '')
        self._addNumberProperty('timeRangeStart', 0)
        self._addNumberProperty('timeRangeEnd', 0)
        self.onOpenPortalClicked = self._addCommand('onOpenPortalClicked')
