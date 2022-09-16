# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/subscriptions_entry_point_model.py
from frameworks.wulf import ViewModel

class SubscriptionsEntryPointModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=1, commands=1):
        super(SubscriptionsEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getIsEnabled(self):
        return self._getBool(0)

    def setIsEnabled(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(SubscriptionsEntryPointModel, self)._initialize()
        self._addBoolProperty('isEnabled', True)
        self.onClick = self._addCommand('onClick')
