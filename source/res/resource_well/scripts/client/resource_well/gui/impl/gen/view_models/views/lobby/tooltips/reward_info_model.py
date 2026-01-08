# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/gen/view_models/views/lobby/tooltips/reward_info_model.py
from frameworks.wulf import ViewModel

class RewardInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(RewardInfoModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(0)

    def setVehicleName(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(RewardInfoModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
