# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_upgrade_info_view_model.py
from frameworks.wulf import ViewModel

class PortalUpgradeInfoViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=0, commands=1):
        super(PortalUpgradeInfoViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(PortalUpgradeInfoViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
