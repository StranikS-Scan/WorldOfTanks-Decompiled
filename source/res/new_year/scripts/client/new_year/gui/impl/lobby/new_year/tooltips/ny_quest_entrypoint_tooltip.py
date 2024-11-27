# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/tooltips/ny_quest_entrypoint_tooltip.py
from frameworks.wulf import View, ViewSettings
from gui.impl.gen import R
from helpers import dependency, time_utils
from helpers.time_utils import ONE_DAY
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_quest_entrypoint_tooltip_model import NyQuestEntrypointTooltipModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.quests.ny_quest_card_model import NyQuestCardModel
from new_year.helpers.server_settings import getNewYearGeneralConfig
from new_year.skeletons.new_year import INewYearController
from new_year.gui.impl.lobby.new_year.quests.ny_quest_helper import updateBattleModes, updateQuests, packNyQuestCardModel
from skeletons.gui.server_events import IEventsCache
LONG_MAX_VALUE = 9223372036854775807L

class NyQuestEntryPointTooltip(View):
    __nyController = dependency.descriptor(INewYearController)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.NYQuestEntryPointTooltip())
        settings.model = NyQuestEntrypointTooltipModel()
        self.__config = getNewYearGeneralConfig()
        self.__dailyPrefix = self.__config.getDailyPrefix()
        self.__weeklyPrefix = self.__config.getWeeklyPrefix()
        self.__mitTime = LONG_MAX_VALUE
        super(NyQuestEntryPointTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyQuestEntryPointTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyQuestEntryPointTooltip, self)._onLoading()
        with self.getViewModel().transaction() as model:
            self.__updateModelImpl(model, model.getWeeklyQuests(), self.__weeklyPrefix)
            self.__updateModelImpl(model, model.getDailyQuests(), self.__dailyPrefix)

    def _finalize(self):
        pass

    def __updateModelImpl(self, model, questArray, questFilter):
        questArray.clear()
        battleTypes = model.getBattleTypes()
        for questID, quest in sorted(self.__eventsCache.getAllQuests().items()):
            if not quest.isStarted():
                continue
            if questID.startswith(questFilter):
                if not quest.isCompleted():
                    questModel = packNyQuestCardModel(quest, NyQuestCardModel())
                    updateQuests(model, quest, questArray, questModel, questFilter)
                    updateBattleModes(quest, battleTypes)
                if self.__mitTime > quest.getFinishTimeLeft():
                    self.__mitTime = quest.getFinishTimeLeft()

        model.setMinResetTimeLeft(self.__mitTime)
        model.setIsLastDay(time_utils.getTimeDeltaFromNowInLocal(self.__nyController.getFinishTime()) < ONE_DAY)
        questArray.invalidate()
        battleTypes.invalidate()
