# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_upgrade_reset_view_model.py
from frameworks.wulf import ViewModel

class PortalUpgradeResetViewModel(ViewModel):
    __slots__ = ('onClose', 'onReset')

    def __init__(self, properties=0, commands=2):
        super(PortalUpgradeResetViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(PortalUpgradeResetViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
        self.onReset = self._addCommand('onReset')
