# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/gen/view_models/views/lobby/tooltips/event_banner_tooltip_model.py
from frameworks.wulf import Array, ViewModel
from resource_well.gui.impl.gen.view_models.views.lobby.tooltips.reward_info_model import RewardInfoModel

class EventBannerTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(EventBannerTooltipModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getStartDate(self):
        return self._getNumber(1)

    def setStartDate(self, value):
        self._setNumber(1, value)

    def getEndDate(self):
        return self._getNumber(2)

    def setEndDate(self, value):
        self._setNumber(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRewardsType():
        return RewardInfoModel

    def _initialize(self):
        super(EventBannerTooltipModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self._addArrayProperty('rewards', Array())
