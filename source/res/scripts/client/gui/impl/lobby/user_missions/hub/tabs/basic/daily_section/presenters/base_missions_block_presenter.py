# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hub/tabs/basic/daily_section/presenters/base_missions_block_presenter.py
import typing
from gui.impl.lobby.user_missions.hangar_widget.utils import DailyMissionItemPacker
from gui.impl.lobby.user_missions.hub.tabs.basic.daily_section.presenters.base_block_presenter import BaseBlockPresenter
from gui.impl.pub.view_impl import TViewModel
from gui.shared.missions.packers.bonus import getDailyMissionsBonusPacker
from gui.shared.missions.packers.events import packQuestBonusModelAndTooltipData
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.basic_missions.common.mission_base_model import MissionBaseModel
    from gui.server_events.event_items import Quest

class BaseMissionsBlockPresenter(BaseBlockPresenter[TViewModel]):

    def __init__(self, model):
        super(BaseMissionsBlockPresenter, self).__init__(model=model)

    def _onLeaveTab(self):
        with self.getViewModel().transaction() as tx:
            self._disableCompletedQuestAnimation(tx)

    def _fillMissionModel(self, mm, quest):
        dailyPacker = DailyMissionItemPacker()
        isCompleted = dailyPacker.packMissionItem(mm, quest)
        questID = quest.getID()
        mm.setId(questID)
        self._tooltipData[questID] = {}
        packQuestBonusModelAndTooltipData(getDailyMissionsBonusPacker(), mm.getBonuses(), quest, tooltipData=self._tooltipData[questID])
        self._rewardsGetterByQuestID[questID] = mm.getBonuses
        return isCompleted

    def _disableCompletedQuestAnimation(self, vm):
        missionsList = vm.getMissionsList()
        for m in missionsList:
            m.setAnimateCompletion(False)
            m.setEarned(0)

        missionsList.invalidate()
