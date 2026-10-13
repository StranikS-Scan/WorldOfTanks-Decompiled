# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/tooltips/fort_rush_daily_quest_tooltip.py
from __future__ import absolute_import
from fort_rush.gui.impl.lobby.bonus_packers import getFortRushMissionBonusPacker
from fort_rush.gui.impl.lobby.quest_packers import FortRushDailyQuestUIDataPacker
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from frameworks.wulf import ViewSettings
from gui.Scaleform.genConsts.MISSIONS_STATES import MISSIONS_STATES
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.widget.widget_quest_model import WidgetQuestModel
from gui.impl.lobby.user_missions.tooltips.quest_tooltip import BaseQuestTooltip
from gui.shared.missions.packers.events import findFirstConditionModel, packQuestBonusModelAndTooltipData
from helpers import dependency
from helpers.time_utils import getDayTimeLeft

class FortRushProgressionQuestTooltip(BaseQuestTooltip):
    __ctrl = dependency.descriptor(IFortRushBattleController)

    def _getSettings(self):
        settings = ViewSettings(R.views.mono.user_missions.tooltips.daily_quest_tooltip())
        settings.model = WidgetQuestModel()
        return settings

    def _getRewardsSortKey(self):
        return None

    def _fillViewModel(self):
        questID = self._quest.getID()
        packer = FortRushDailyQuestUIDataPacker(self._quest)
        fullQuestModel = packer.pack()
        isCompleted = fullQuestModel.getStatus().value == MISSIONS_STATES.COMPLETED
        timeLeft = int(getDayTimeLeft())
        with self.viewModel.transaction() as vm:
            vm.setId(questID)
            vm.setMissionType('battleQuest')
            vm.setIsCompleted(isCompleted)
            vm.setIcon(fullQuestModel.getIcon())
            vm.setIsLocked(self._quest.getData().get('meta', {}).get('locked', False))
            vm.setDescription(fullQuestModel.getDescription())
            vm.setCountdown(timeLeft)
            conditionModel = self.__getFirstConditionModel(fullQuestModel)
            if conditionModel is not None:
                vm.setCurrentProgress(conditionModel.getCurrent())
                vm.setTotalProgress(conditionModel.getTotal())
                vm.setEarned(conditionModel.getEarned())
            packQuestBonusModelAndTooltipData(getFortRushMissionBonusPacker(), vm.getBonuses(), self._quest)
        return

    @staticmethod
    def __getFirstConditionModel(questModel):
        postBattleModel = findFirstConditionModel(questModel.postBattleCondition)
        bonusConditionModel = findFirstConditionModel(questModel.bonusCondition)
        return postBattleModel if postBattleModel else bonusConditionModel
