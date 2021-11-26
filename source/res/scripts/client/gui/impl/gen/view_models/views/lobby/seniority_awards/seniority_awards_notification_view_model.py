# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/seniority_awards_notification_view_model.py
from frameworks.wulf import ViewModel

class SeniorityAwardsNotificationViewModel(ViewModel):
    __slots__ = ('onOpenShopClick', 'onCloseAction')

    def __init__(self, properties=2, commands=2):
        super(SeniorityAwardsNotificationViewModel, self).__init__(properties=properties, commands=commands)

    def getSpecialCurrencyCount(self):
        return self._getNumber(0)

    def setSpecialCurrencyCount(self, value):
        self._setNumber(0, value)

    def getDate(self):
        return self._getNumber(1)

    def setDate(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(SeniorityAwardsNotificationViewModel, self)._initialize()
        self._addNumberProperty('specialCurrencyCount', -1)
        self._addNumberProperty('date', -1)
        self.onOpenShopClick = self._addCommand('onOpenShopClick')
        self.onCloseAction = self._addCommand('onCloseAction')
