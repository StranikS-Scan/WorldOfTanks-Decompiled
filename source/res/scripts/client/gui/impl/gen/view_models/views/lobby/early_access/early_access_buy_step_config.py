# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/early_access_buy_step_config.py
from frameworks.wulf import ViewModel

class EarlyAccessBuyStepConfig(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(EarlyAccessBuyStepConfig, self).__init__(properties=properties, commands=commands)

    def getHasVehicleInReward(self):
        return self._getBool(0)

    def setHasVehicleInReward(self, value):
        self._setBool(0, value)

    def getVehicleRewardTooltipId(self):
        return self._getString(1)

    def setVehicleRewardTooltipId(self, value):
        self._setString(1, value)

    def getVehicleRewardTooltipContentId(self):
        return self._getString(2)

    def setVehicleRewardTooltipContentId(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(EarlyAccessBuyStepConfig, self)._initialize()
        self._addBoolProperty('hasVehicleInReward', False)
        self._addStringProperty('vehicleRewardTooltipId', '')
        self._addStringProperty('vehicleRewardTooltipContentId', '')
