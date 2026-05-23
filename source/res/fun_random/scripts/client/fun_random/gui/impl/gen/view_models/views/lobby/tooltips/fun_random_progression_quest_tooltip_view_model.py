# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/tooltips/fun_random_progression_quest_tooltip_view_model.py
from frameworks.wulf import ViewModel
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_quest_card_model import FunRandomQuestCardModel
from fun_random.gui.impl.gen.view_models.views.lobby.tooltips.fun_random_base_quest_tooltip_view_model import FunRandomBaseQuestTooltipViewModel

class FunRandomProgressionQuestTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(FunRandomProgressionQuestTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def quest(self):
        return self._getViewModel(0)

    @staticmethod
    def getQuestType():
        return FunRandomQuestCardModel

    @property
    def tooltip(self):
        return self._getViewModel(1)

    @staticmethod
    def getTooltipType():
        return FunRandomBaseQuestTooltipViewModel

    def _initialize(self):
        super(FunRandomProgressionQuestTooltipViewModel, self)._initialize()
        self._addViewModelProperty('quest', FunRandomQuestCardModel())
        self._addViewModelProperty('tooltip', FunRandomBaseQuestTooltipViewModel())
