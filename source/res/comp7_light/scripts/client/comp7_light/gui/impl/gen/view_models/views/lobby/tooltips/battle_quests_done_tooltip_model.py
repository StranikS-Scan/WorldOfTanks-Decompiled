# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/gen/view_models/views/lobby/tooltips/battle_quests_done_tooltip_model.py
from frameworks.wulf import ViewModel
from comp7_light.gui.impl.gen.view_models.views.lobby.season_model import SeasonModel

class BattleQuestsDoneTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BattleQuestsDoneTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def season(self):
        return self._getViewModel(0)

    @staticmethod
    def getSeasonType():
        return SeasonModel

    def getCountdown(self):
        return self._getNumber(1)

    def setCountdown(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(BattleQuestsDoneTooltipModel, self)._initialize()
        self._addViewModelProperty('season', SeasonModel())
        self._addNumberProperty('countdown', 0)
