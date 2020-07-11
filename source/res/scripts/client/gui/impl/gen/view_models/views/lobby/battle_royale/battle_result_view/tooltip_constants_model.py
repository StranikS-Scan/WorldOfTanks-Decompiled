# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_royale/battle_result_view/tooltip_constants_model.py
from frameworks.wulf import ViewModel

class TooltipConstantsModel(ViewModel):
    __slots__ = ()
    ACHIEVEMENT_TOOLTIP = 'battleStatsAchievementData'
    QUEST_COMPLETE_TOOLTIP = 'QuestCompletedTooltip'
    BONUS_TOOLTIP = 'bonusTooltip'

    def __init__(self, properties=0, commands=0):
        super(TooltipConstantsModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(TooltipConstantsModel, self)._initialize()
