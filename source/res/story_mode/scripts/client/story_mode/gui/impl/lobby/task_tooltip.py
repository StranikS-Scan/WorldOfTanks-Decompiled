# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/task_tooltip.py
import typing
from datetime import datetime
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.server_events.bonuses import getNonQuestBonuses
from story_mode.gui.impl.gen.view_models.views.lobby.mission_task_tooltip_model import MissionTaskTooltipModel
from story_mode.gui.impl.gen.view_models.views.lobby.mission_task_tooltip_model import TaskStateEnum
from story_mode.gui.shared.packers.bonus import getSMBonusPacker
from story_mode.gui.story_mode_gui_constants import BONUS_ORDER
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
    from gui.impl.gen_utils import DynAccessor

class TaskTooltip(ViewImpl):

    def __init__(self, title, state, rewards, unlockDate):
        settings = ViewSettings(R.views.story_mode.lobby.TaskTooltip(), model=MissionTaskTooltipModel())
        super(TaskTooltip, self).__init__(settings)
        self._title = title
        self._state = state
        self._rewards = []
        self._unlockDate = unlockDate
        for rewardName, rewardData in rewards.iteritems():
            self._rewards.extend(getNonQuestBonuses(rewardName, rewardData))

        self._rewards.sort(key=self._bonusesSortFunction)
        self.__packer = getSMBonusPacker()

    @property
    def viewModel(self):
        return super(TaskTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TaskTooltip, self)._onLoading(*args, **kwargs)
        if self._state == TaskStateEnum.LOCKED:
            self.viewModel.setTitle(R.strings.sm_lobby.tooltips.task.condition.locked())
        elif self._title.isValid():
            self.viewModel.setTitle(self._title())
        utcnow = datetime.utcnow()
        if self._unlockDate:
            self.viewModel.setSecondsBeforeUnlock(max(int((self._unlockDate - utcnow).total_seconds()), 0))
        self.viewModel.setTaskState(self._state)
        rewardsArray = self.viewModel.getRewards()
        rewardsArray.clear()
        for bonus in self._rewards:
            bonusList = self.__packer.pack(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndex)
                rewardsArray.addViewModel(item)

    @staticmethod
    def _bonusesSortFunction(bonus):
        name = bonus.getName()
        return BONUS_ORDER.index(name) if name in BONUS_ORDER else len(BONUS_ORDER) + 1
