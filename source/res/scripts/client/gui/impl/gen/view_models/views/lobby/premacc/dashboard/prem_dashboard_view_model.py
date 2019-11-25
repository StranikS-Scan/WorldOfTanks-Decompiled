# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/prem_dashboard_view_model.py
from frameworks.wulf import ViewModel

class PremDashboardViewModel(ViewModel):
    __slots__ = ('onCloseAction', 'onInitialized')

    def __init__(self, properties=0, commands=2):
        super(PremDashboardViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(PremDashboardViewModel, self)._initialize()
        self.onCloseAction = self._addCommand('onCloseAction')
        self.onInitialized = self._addCommand('onInitialized')
