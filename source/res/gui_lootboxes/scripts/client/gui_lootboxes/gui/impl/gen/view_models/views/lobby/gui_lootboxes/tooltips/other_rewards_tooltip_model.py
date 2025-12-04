# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/other_rewards_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class OtherRewardType(Enum):
    ACCOUNTCUSTOMIZATIONS = 'accountCustomizations'
    BOOSTERS = 'boosters'
    CREW = 'crew'
    VEHICLECUSTOMIZATIONS = 'vehicleCustomizations'
    EQUIPMENTS = 'equipments'
    FEATUREITEMS = 'featureItems'
    LOOTBOXES = 'lootboxes'


class OtherRewardsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(OtherRewardsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return OtherRewardType(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def _initialize(self):
        super(OtherRewardsTooltipModel, self)._initialize()
        self._addStringProperty('type')
