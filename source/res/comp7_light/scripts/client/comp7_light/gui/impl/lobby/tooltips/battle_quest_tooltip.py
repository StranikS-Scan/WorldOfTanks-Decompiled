# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/tooltips/battle_quest_tooltip.py
from comp7.gui.impl.lobby.comp7_helpers.comp7_bonus_packer import packQuestBonuses
from comp7_light.gui.impl.lobby.comp7_light_helpers.comp7_light_mission_packer import packMissionItem
from comp7_light.gui.impl.lobby.comp7_light_helpers.comp7_light_packers import getComp7LightBonusPacker
from frameworks.wulf import ViewSettings
from frameworks.wulf.view.array import fillViewModelsArray
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.widget.widget_quest_model import WidgetQuestModel
from gui.impl.lobby.user_missions.tooltips.quest_tooltip import BaseQuestTooltip
from gui.server_events.events_helpers import EventInfoModel
from gui.shared.missions.packers.events import DailyQuestUIDataPacker

class BattleQuestTooltip(BaseQuestTooltip):

    def _getSettings(self):
        settings = ViewSettings(R.views.comp7_light.mono.lobby.tooltips.battle_quest_tooltip())
        settings.model = WidgetQuestModel()
        return settings

    def _fillViewModel(self):
        bonusPacker = getComp7LightBonusPacker()
        packedBonuses, _ = packQuestBonuses(self._quest.getBonuses(), bonusPacker)
        with self.viewModel.transaction() as tx:
            packMissionItem(tx, self._quest, DailyQuestUIDataPacker)
            fillViewModelsArray(packedBonuses, tx.getBonuses())
            tx.setCountdown(EventInfoModel.getDailyProgressResetTimeDelta())

    def _getRewardsSortFunc(self):
        return None
