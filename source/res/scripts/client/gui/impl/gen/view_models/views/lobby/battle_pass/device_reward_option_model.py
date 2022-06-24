# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/device_reward_option_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.kpi_description_model import KpiDescriptionModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_option_model import RewardOptionModel

class DeviceRewardOptionModel(RewardOptionModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(DeviceRewardOptionModel, self).__init__(properties=properties, commands=commands)

    @property
    def kpiDescriptions(self):
        return self._getViewModel(6)

    @staticmethod
    def getKpiDescriptionsType():
        return KpiDescriptionModel

    def getEffect(self):
        return self._getString(7)

    def setEffect(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(DeviceRewardOptionModel, self)._initialize()
        self._addViewModelProperty('kpiDescriptions', UserListModel())
        self._addStringProperty('effect', '')
