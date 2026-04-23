# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/quests_widget_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.quests_widget_tooltip_model import QuestsWidgetTooltipModel
from historical_battles.gui.server_events.battle_quests.quest_model_helpers import fillQuestModel
from historical_battles.gui.server_events.battle_quests.quests_container import getHBQuestsContainer, HBQuestGroup

class QuestsWidgetTooltip(ViewImpl):
    __slots__ = ('__questId', '__frontName')

    def __init__(self, questId, frontName):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.QuestsWidgetTooltip())
        settings.model = QuestsWidgetTooltipModel()
        self.__questId = questId
        self.__frontName = frontName
        super(QuestsWidgetTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(QuestsWidgetTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(QuestsWidgetTooltip, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def __updateModel(self):
        questsContainer = getHBQuestsContainer()
        quest = dict(questsContainer.getQuests()).get(self.__questId)
        if quest:
            isDaily = HBQuestGroup.DAILY.value in quest.getGroupID()
            with self.viewModel.transaction() as model:
                model.setFrontName(self.__frontName)
                fillQuestModel(quest, model.questTooltipModel, isDaily)
