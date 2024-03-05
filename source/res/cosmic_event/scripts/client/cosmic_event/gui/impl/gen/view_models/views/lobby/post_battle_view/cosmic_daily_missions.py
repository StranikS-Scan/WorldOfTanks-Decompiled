# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/post_battle_view/cosmic_daily_missions.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.missions.widget.widget_quest_model import WidgetQuestModel

class CosmicDailyMissions(WidgetQuestModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(CosmicDailyMissions, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(7)

    def setRewards(self, value):
        self._setArray(7, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(CosmicDailyMissions, self)._initialize()
        self._addArrayProperty('rewards', Array())
