# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/level_rewards_group_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class LevelRewardsGroupModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(LevelRewardsGroupModel, self).__init__(properties=properties, commands=commands)

    def getOverlayType(self):
        return self._getString(8)

    def setOverlayType(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(LevelRewardsGroupModel, self)._initialize()
        self._addStringProperty('overlayType', '')
