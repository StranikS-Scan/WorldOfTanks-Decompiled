# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/battle_result_stat_tooltip_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from story_mode.gui.impl.gen.view_models.views.lobby.detailed_stat_model import DetailedStatModel

class StatEnum(Enum):
    MISSIONS = 'missions'
    ASSIST = 'assist'
    KILLS = 'kills'
    DAMAGE = 'damage'
    ARMOR_USE = 'armorUse'


class BattleResultStatTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BattleResultStatTooltipModel, self).__init__(properties=properties, commands=commands)

    def getStat(self):
        return StatEnum(self._getString(0))

    def setStat(self, value):
        self._setString(0, value.value)

    def getDetailedStats(self):
        return self._getArray(1)

    def setDetailedStats(self, value):
        self._setArray(1, value)

    @staticmethod
    def getDetailedStatsType():
        return DetailedStatModel

    def _initialize(self):
        super(BattleResultStatTooltipModel, self)._initialize()
        self._addStringProperty('stat')
        self._addArrayProperty('detailedStats', Array())
