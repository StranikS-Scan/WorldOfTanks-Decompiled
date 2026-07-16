# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/battle_results/missions_progress/comp7_light_progression_quests_progress.py
from __future__ import absolute_import
from gui.battle_results.pbs_helpers.common import getBattleResults
from gui.battle_results.progress.progress_helpers import getReceivedTokensInfo
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.common.missions.event_model import EventStatus
from gui.impl.gen.view_models.views.lobby.battle_results.progression.common_battle_quest_progress_model import CommonBattleQuestProgressModel
from gui.impl.gen.view_models.views.lobby.battle_results.progression.common_battle_quests_progress_model import CommonBattleQuestsProgressModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.battle_results.missions_progress.progression_presenter_interface import IProgressionCategoryPresenter
from gui.impl.lobby.battle_results.missions_progress.rewards_helper import packBonusesWithActualTokensConvertion
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.server_events import conditions
from gui.shared.missions.packers.events import TokenUIDataPacker, BattleQuestUIDataPacker
from comp7_light.gui.impl.lobby.comp7_light_helpers.comp7_light_packers import getComp7LightBonusPacker
from quest_xml_source import MAX_BONUS_LIMIT
from comp7_light.gui.shared.event_dispatcher import showComp7LightProgressionView
import constants

class Comp7LightProgressionQuestsPresenter(ViewComponent[CommonBattleQuestsProgressModel], IProgressionCategoryPresenter):
    _PLUGIN_PATH = 'coui://comp7_light/gui/gameface/_dist/production/mono/plugins/lobby/progression_quests/progression_quests.js'

    def __init__(self, categoryProgressFilter, arenaUniqueID, allCommonQuests):
        super(Comp7LightProgressionQuestsPresenter, self).__init__(model=CommonBattleQuestsProgressModel)
        self.__categoryProgressFilter = categoryProgressFilter
        self.__arenaUniqueID = arenaUniqueID
        self.__allCommonQuests = allCommonQuests
        self.__progress = None
        self.__tooltipData = {}
        self.__bonusesModel = {}
        return

    @classmethod
    def getPathToResource(cls):
        return cls._PLUGIN_PATH

    @classmethod
    def getViewAlias(cls):
        return R.aliases.comp7_light.shared.BattleResultsProgressionQuests()

    @property
    def viewModel(self):
        return super(Comp7LightProgressionQuestsPresenter, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getTooltipData(event)
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow(), event)
                window.load()
                return window
        return super(Comp7LightProgressionQuestsPresenter, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
            showFromIndex = event.getArgument('showFromIndex')
            questId = event.getArgument('questId')
            for data, _, _, _, _ in self.__progress:
                if questId == data.getID():
                    bonuses = self.__bonusesModel[questId]
                    return AdditionalRewardsTooltip(bonuses[int(showFromIndex):])

        return super(Comp7LightProgressionQuestsPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def _finalize(self):
        self.__tooltipData.clear()
        self.__tooltipData = None
        self.__bonusesModel.clear()
        self.__bonusesModel = None
        self.__progress = None
        self.__categoryProgressFilter = None
        self.__arenaUniqueID = None
        self.__allCommonQuests = None
        super(Comp7LightProgressionQuestsPresenter, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onNavigate, self.__onNavigate),)

    def _onLoading(self, *args, **kwargs):
        super(Comp7LightProgressionQuestsPresenter, self)._onLoading(*args, **kwargs)
        self._updateProgress()
        if not self.__progress:
            return
        self._updateModel()
        plugins = self.getParentView().viewModel.getPathToPlugins()
        plugins.set(self.getViewAlias(), self.getPathToResource())

    def _updateProgress(self):
        battleResults = getBattleResults(self.__arenaUniqueID)
        if battleResults:
            self.__progress = self.__categoryProgressFilter(battleResults.reusable, self.__allCommonQuests)

    def _updateModel(self):
        questTokensConvertion, questTokensCount = getReceivedTokensInfo(self.__arenaUniqueID)
        with self.viewModel.transaction():
            quests = self.viewModel.getCommonQuests()
            quests.clear()
            for event, pCur, pPrev, _, isCompleted in self.__progress:
                questModel = self.__createModel(event, pCur, pPrev, isCompleted, questTokensConvertion, questTokensCount)
                if questModel:
                    quests.addViewModel(questModel)

            quests.invalidate()

    def __createModel(self, event, pCur, pPrev, isCompleted, questTokensConvertion, questTokensCount):
        eventID = event.getID()
        self.__tooltipData[eventID] = {}
        self.__bonusesModel[eventID] = {}
        model = CommonBattleQuestProgressModel()
        if event.getType() == constants.EVENT_TYPE.TOKEN_QUEST:
            packer = TokenUIDataPacker(event)
            packer.pack(model)
        elif event.getType() in constants.EVENT_TYPE.LIKE_BATTLE_QUESTS:
            packer = BattleQuestUIDataPacker(event)
            packer.pack(model)
        else:
            return None
        bonusPacker = getComp7LightBonusPacker()
        packBonusesWithActualTokensConvertion(pCur, model, event, questTokensConvertion, questTokensCount, self.__tooltipData[eventID], bonusPacker)
        self.__bonusesModel[eventID] = model.getBonuses()
        model.setGuiDisabled(event.isGuiDisabled())
        model.setHidden(event.isHidden())
        model.setAvailable(event.isRawAvailable())
        bonusLimit = event.bonusCond.getBonusLimit()
        model.setMaxCompletionCount(bonusLimit)
        model.setCurrentCompletionCount(event.getBonusCount(progress=pCur))
        model.setDefaultMaxCompletionCount(MAX_BONUS_LIMIT)
        if isCompleted:
            model.setStatus(EventStatus.DONE)
        elif event.isAvailable():
            model.setStatus(EventStatus.ACTIVE)
        else:
            model.setStatus(EventStatus.LOCKED)
        model.setNavigationEnabled(True)
        condsRoot = event.bonusCond.getConditions()
        if condsRoot.isEmpty():
            return model
        else:
            index = 0
            items = model.bonusCondition.getItems()
            for cond in condsRoot.items:
                if isinstance(cond, conditions._Cumulativable):
                    for curProg, totalProg, diff, _ in cond.getProgressPerGroup(pCur, pPrev, True).values():
                        item = items[index]
                        item.setEarned(diff)
                        item.setCurrent(curProg)
                        item.setTotal(totalProg)
                        index += 1

            return model

    def __getTooltipData(self, event):
        missionParam = event.getArgument('tooltipId', '')
        missionParams = missionParam.rsplit(':', 1)
        if len(missionParams) != 2:
            return self.__tooltipData.get(missionParam)
        missionId, tooltipId = missionParams
        tooltipsData = self.__tooltipData.get(missionId, {})
        return tooltipsData.get(tooltipId, {})

    @args2params(str, int)
    def __onNavigate(self, questId, eventType):
        showComp7LightProgressionView()
