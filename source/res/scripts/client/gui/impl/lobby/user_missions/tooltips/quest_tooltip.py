# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/tooltips/quest_tooltip.py
from abc import ABCMeta
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.widget.widget_quest_model import WidgetQuestModel
from gui.impl.pub import ViewImpl
from gui.shared.missions.packers.bonus import weeklyBonusSort
from gui.shared.missions.packers.events import packQuestBonusModel
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class BaseQuestTooltip(ViewImpl):
    __metaclass__ = ABCMeta
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, quest):
        settings = self._getSettings()
        self._quest = quest
        self._tooltipData = {}
        super(BaseQuestTooltip, self).__init__(settings)

    def _getSettings(self):
        raise NotImplementedError

    def _finalize(self):
        self._quest = None
        super(BaseQuestTooltip, self)._finalize()
        return

    @property
    def viewModel(self):
        return super(BaseQuestTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BaseQuestTooltip, self)._onLoading()
        self._fillViewModel()

    def _fillViewModel(self):
        with self.viewModel.transaction() as vm:
            vm.setId(self._quest.itemId)
            vm.setMissionType(str(self._quest.itemType))
            vm.setCountdown(int(self._quest.countdown))
            vm.setIsCompleted(bool(self._quest.isCompleted))
            missionPacker = self._quest.getMissionPacker()
            missionPacker.packMissionItem(vm, self._quest.rawData)
            missionPacker.packSpecificMissionItem(vm, self._quest)
            self._packBonuses(vm, self._quest.rawData, self._quest.getBonusPacker())

    def _packBonuses(self, model, data, bonusPacker):
        bonuses = model.getBonuses()
        bonuses.clear()
        packQuestBonusModel(quest=data, packer=bonusPacker, array=bonuses, sort=self._getRewardsSortFunc())

    def _getRewardsSortFunc(self):
        raise NotImplementedError


class DailyQuestTooltip(BaseQuestTooltip):

    def _getSettings(self):
        settings = ViewSettings(R.views.mono.user_missions.tooltips.daily_quest_tooltip())
        settings.model = WidgetQuestModel()
        return settings

    def _getRewardsSortFunc(self):
        return None


class WeeklyQuestTooltip(BaseQuestTooltip):

    def _getSettings(self):
        settings = ViewSettings(R.views.mono.user_missions.tooltips.weekly_quest_tooltip())
        settings.model = WidgetQuestModel()
        return settings

    def _getRewardsSortFunc(self):
        return weeklyBonusSort
