# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/wot_plus_subscription_bonus_model.py
from frameworks.wulf import ViewModel

class WotPlusSubscriptionBonusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(WotPlusSubscriptionBonusModel, self).__init__(properties=properties, commands=commands)

    def getLabel(self):
        return self._getString(0)

    def setLabel(self, value):
        self._setString(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(WotPlusSubscriptionBonusModel, self)._initialize()
        self._addStringProperty('label', '')
        self._addStringProperty('type', '')
