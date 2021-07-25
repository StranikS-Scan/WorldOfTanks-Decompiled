# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_royale/tooltips/battle_pass_points_sources_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.battle_royale.tooltips.battle_pass_points_sources_tooltip_view_model import BattlePassPointsSourcesTooltipViewModel
from gui.impl.gen.view_models.views.lobby.battle_royale.tooltips.battle_pass_quests_points import BattlePassQuestsPoints
from gui.server_events.battle_royale_formatters import BRSections
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.server_events import IEventsCache
from helpers import dependency

class BattlePassPointsSourcesTooltipView(ViewImpl):
    __slots__ = ('__data',)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, data):
        settings = ViewSettings(R.views.lobby.battle_royale.tooltips.BattlePassPointsSourcesTooltipView())
        settings.model = BattlePassPointsSourcesTooltipViewModel()
        super(BattlePassPointsSourcesTooltipView, self).__init__(settings)
        self.__data = data

    @property
    def viewModel(self):
        return super(BattlePassPointsSourcesTooltipView, self).getViewModel()

    def _finalize(self):
        super(BattlePassPointsSourcesTooltipView, self)._finalize()
        self.__data = None
        return

    def _onLoading(self, *args, **kwargs):
        super(BattlePassPointsSourcesTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setBattlePoints(self.__data[BRSections.PERSONAL][BRSections.BATTLE_PASS]['earnedPoints'])
            questPointList = model.getQuestPoints()
            questPointList.clear()
            completedQuests = self.__data[BRSections.PERSONAL][BRSections.REWARDS]['completedQuests']
            allQuests = self.__eventsCache.getAllQuests()
            for qId in completedQuests:
                quest = allQuests.get(qId)
                for bonus in quest.getBonuses():
                    if bonus.getName() == 'battlePassPoints':
                        questModel = BattlePassQuestsPoints()
                        questModel.setCount(bonus.getCount())
                        questModel.setName(quest.getUserName())
                        questPointList.addViewModel(questModel)

            questPointList.invalidate()
