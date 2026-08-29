# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/common_stats_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.postbattle.detailed_personal_efficiency_model import DetailedPersonalEfficiencyModel
from gui.impl.gen.view_models.views.lobby.postbattle.general_info_model import GeneralInfoModel
from gui.impl.gen.view_models.views.lobby.postbattle.rewards_model import RewardsModel

class CommonStatsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(CommonStatsModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardsType():
        return RewardsModel

    @property
    def generalInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getGeneralInfoType():
        return GeneralInfoModel

    @property
    def detailedEfficiency(self):
        return self._getViewModel(2)

    @staticmethod
    def getDetailedEfficiencyType():
        return DetailedPersonalEfficiencyModel

    def getTitle(self):
        return self._getString(3)

    def setTitle(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(CommonStatsModel, self)._initialize()
        self._addViewModelProperty('rewards', RewardsModel())
        self._addViewModelProperty('generalInfo', GeneralInfoModel())
        self._addViewModelProperty('detailedEfficiency', DetailedPersonalEfficiencyModel())
        self._addStringProperty('title', '')
