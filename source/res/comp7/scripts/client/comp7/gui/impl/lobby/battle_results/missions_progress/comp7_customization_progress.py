# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/battle_results/missions_progress/comp7_customization_progress.py
from __future__ import absolute_import
import typing
from shared_utils import first
from comp7.gui.impl.gen.view_models.views.lobby.battle_results.comp7_customization_quest_progress_model import Comp7CustomizationQuestProgressModel
from comp7.gui.impl.gen.view_models.views.lobby.battle_results.comp7_customization_quests_progress_model import Comp7CustomizationQuestsProgressModel
from comp7.gui.impl.lobby.comp7_helpers.comp7_c11n_helpers import getComp7ProgressionStyle
from comp7.gui.shared.missions.packers.events import Comp7WeeklyQuestPacker
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_results.pbs_helpers.common import getBattleResults
from gui.impl.backport.backport_tooltip import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.lobby.battle_results.missions_progress.progression_presenter_interface import IProgressionCategoryPresenter
from gui.impl.pub.view_component import ViewComponent
from gui.server_events import conditions
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization import CustomizationTooltipContext
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from comp7.gui.impl.gen.view_models.views.lobby.comp7_battle_results_view_model import Comp7BattleResultsViewModel

class Comp7CustomizationProgressPresenter(ViewComponent[Comp7CustomizationQuestsProgressModel], IProgressionCategoryPresenter):
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, categoryProgressFilter, arenaUniqueID, allCommonQuests):
        super(Comp7CustomizationProgressPresenter, self).__init__(model=Comp7CustomizationQuestsProgressModel)
        self.__categoryProgressFilter = categoryProgressFilter
        self.__arenaUniqueID = arenaUniqueID
        self.__allCommonQuests = allCommonQuests
        self.__progress = None
        return

    @classmethod
    def getPathToResource(cls):
        return Comp7CustomizationQuestsProgressModel.PATH

    @classmethod
    def getViewAlias(cls):
        return R.aliases.comp7.shared.BattleResultsCustomizationQuests()

    @property
    def viewModel(self):
        return super(Comp7CustomizationProgressPresenter, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TOOLTIPS_CONSTANTS.TECH_CUSTOMIZATION_ITEM:
                itemCD = int(event.getArgument('customizationId'))
                level = int(event.getArgument('progressionLevel'))
                tooltipData = createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=CustomizationTooltipContext(itemCD, -1, True, level))
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(Comp7CustomizationProgressPresenter, self).createToolTip(event)

    def _finalize(self):
        self.__categoryProgressFilter = None
        self.__arenaUniqueID = None
        self.__allCommonQuests = None
        self.__progress = None
        super(Comp7CustomizationProgressPresenter, self)._finalize()
        return

    def _onLoading(self, *args, **kwargs):
        super(Comp7CustomizationProgressPresenter, self)._onLoading(*args, **kwargs)
        battleResults = getBattleResults(self.__arenaUniqueID)
        if not battleResults:
            return
        self.__progress = self.__categoryProgressFilter(battleResults.reusable, self.__allCommonQuests)
        if not self.__progress:
            return
        self.__progress.sort(key=lambda qData: (qData[4], qData[0].getID()))
        self._updateModel()
        parentModel = self.getParentView().viewModel
        plugins = parentModel.getPathToPlugins()
        plugins.set(self.getViewAlias(), self.getPathToResource())

    def _updateModel(self):
        with self.viewModel.transaction():
            questsModel = self.viewModel.getCustomizationQuests()
            questsModel.clear()
            for quest, progressCur, progressPrev, _, isCompleted in self.__progress:
                questModel = self.__createModel(quest, progressCur, progressPrev, isCompleted)
                if questModel:
                    questsModel.addViewModel(questModel)

            questsModel.invalidate()

    def __createModel(self, quest, pCur, pPrev, isCompleted):
        questID = quest.getID()
        model = Comp7CustomizationQuestProgressModel()
        model.setIsCompleted(isCompleted)
        intCD, customizationIcon, customizationLevel = self.__getCustomizationData(questID)
        if intCD is not None:
            model.setCustomizationIconKey(customizationIcon)
            model.setCustomizationId(intCD)
            model.setProgressionLevel(customizationLevel)
        iconKey, _, totalProgress, description = Comp7WeeklyQuestPacker().getData(quest)
        currentProgress, diff = self.__getEarnedPoints(quest, pCur, pPrev, isCompleted, totalProgress)
        model.setIconKey(iconKey)
        model.setCurrentProgress(currentProgress)
        model.setTotalProgress(totalProgress)
        model.setDescription(description)
        model.setEarned(diff)
        return model

    def __getEarnedPoints(self, data, pCur, pPrev, isCompleted, totalProgress):
        if isCompleted:
            return (totalProgress, pCur.get(None, {}).get('bonusCount', 0))
        else:
            for cond in data.bonusCond.getConditions().items:
                if isinstance(cond, conditions.Cumulativable):
                    progressData = first(cond.getProgressPerGroup(pCur, pPrev, True).values())
                    if progressData:
                        current, _, diff, _ = progressData
                    else:
                        current = 0
                        diff = 0
                    return (current, diff)

            return (0, 0)

    def __getCustomizationData(self, questID):
        style = getComp7ProgressionStyle()
        for item in style.alternateItems:
            quests = item.getUnlockingQuests()
            for quest in quests or ():
                if quest.getID() == questID:
                    icon = item.texture.split('/')[-1].split('.')[0]
                    level = item.descriptor.requiredTokenCount if item.itemTypeID == GUI_ITEM_TYPE.EMBLEM else 0
                    return (item.intCD, icon, level)

        return (None, None)
