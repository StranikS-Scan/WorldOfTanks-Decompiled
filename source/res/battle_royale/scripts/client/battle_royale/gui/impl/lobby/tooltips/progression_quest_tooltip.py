# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/tooltips/progression_quest_tooltip.py
from battle_royale_progression.gui.impl.lobby.views.bonus_packer import getBonusPacker, packMissionItem, packQuestBonuses
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.widget.widget_quest_model import WidgetQuestModel
from gui.impl.lobby.user_missions.tooltips.quest_tooltip import BaseQuestTooltip
from frameworks.wulf import ViewSettings
from frameworks.wulf.view.array import fillViewModelsArray
from gui.shared.missions.packers.events import DailyQuestUIDataPacker
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

class BattleRoyaleProgressionQuestTooltip(BaseQuestTooltip):
    __battleRoyale = dependency.descriptor(IBattleRoyaleController)

    def _getSettings(self):
        settings = ViewSettings(R.views.battle_royale.mono.lobby.tooltips.progression_quest())
        settings.model = WidgetQuestModel()
        return settings

    def _fillViewModel(self):
        questsTimer = self.__battleRoyale.getQuestsTimerLeft()
        with self.viewModel.transaction() as vm:
            vm.setId(self._quest.getID())
            vm.setCountdown(questsTimer)
            bonusPacker = getBonusPacker()
            packedBonuses, _ = packQuestBonuses(self._quest.getBonuses(), bonusPacker)
            fillViewModelsArray(packedBonuses, vm.getBonuses())
            packMissionItem(vm, self._quest, DailyQuestUIDataPacker)

    def _getRewardsSortFunc(self):
        return None
