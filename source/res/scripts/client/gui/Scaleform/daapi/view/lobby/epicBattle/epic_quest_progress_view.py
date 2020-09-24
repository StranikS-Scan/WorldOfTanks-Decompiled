# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/epic_quest_progress_view.py
from helpers import dependency
from frameworks.wulf import ViewSettings, ViewFlags, Array
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.epic.epic_quest_progress_model import EpicQuestProgressModel
from gui.impl.gen.view_models.views.lobby.epic.quest_progress_item_model import QuestProgressItemModel
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, events
from shared_utils import findFirst
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.game_control import IEventProgressionController
from skeletons.gui.lobby_context import ILobbyContext
_BONUS_CRYSTAL = 'crystal'
_BONUS_GOODIES = 'goodies'

class EpicQuestProgressInject(InjectComponentAdaptor):

    def __init__(self):
        super(EpicQuestProgressInject, self).__init__()
        self._view = None
        return

    def updateQuestsInfo(self, arenaUniqueID):
        if self._view is not None:
            self._view.updateQuestsInfo(arenaUniqueID)
        return

    def _makeInjectView(self):
        self._view = EpicQuestProgressView()
        return self._view

    def _dispose(self):
        super(EpicQuestProgressInject, self)._dispose()
        self._view = None
        return


class EpicQuestProgressView(ViewImpl):
    __slots__ = ('__arenaUniqueID', '__maxEpicLevel', '__currentEpicLevel')
    __battleResults = dependency.descriptor(IBattleResultsService)
    __goodiesCache = dependency.descriptor(IGoodiesCache)
    __eventProgression = dependency.descriptor(IEventProgressionController)
    __lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.epic.PostbattleQuestProgress())
        settings.flags = ViewFlags.COMPONENT
        settings.model = EpicQuestProgressModel()
        super(EpicQuestProgressView, self).__init__(settings)
        self.__arenaUniqueID = None
        self.__maxEpicLevel = self.__lobbyCtx.getServerSettings().epicMetaGame.metaLevel.get('maxLevel', 0)
        levelInfo = self.__eventProgression.getPlayerLevelInfo()
        self.__currentEpicLevel = levelInfo.currentLevel
        return

    @property
    def viewModel(self):
        return super(EpicQuestProgressView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.epic.tooltips.QuestProgressTooltip():
            questId = event.getArgument('questId')
            quest = findFirst(lambda q: q.getId() == questId, self.viewModel.getQuests())
            return EpicQuestRewardTooltip(quest)

    def _initialize(self, *args, **kwargs):
        self.viewModel.showQuestById += self.__onShowQuestById

    def _finalize(self):
        self.viewModel.showQuestById -= self.__onShowQuestById

    def __onShowQuestById(self, args):
        questId = args.get('id')
        eventType = args.get('eventType')
        g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.BATTLE_RESULTS_SHOW_QUEST, ctx={'questId': questId,
         'eventType': eventType}))

    def __getRewards(self, quest):
        bonuses = quest.getBonuses()
        rewards = []
        for q in bonuses:
            if q.getName() == _BONUS_CRYSTAL:
                val = str(q.getValue()) + '%(crystals)'
                rewards.append(val)
            if q.getName() == _BONUS_GOODIES:
                goodieDict = q.getValue()
                if goodieDict:
                    booster = self.__goodiesCache.getBooster(next(iter(goodieDict)))
                    if booster is not None:
                        goodiesEffectTime = booster.getEffectTimeStr(hoursOnly=True)
                        goodiesEffectValue = booster.getFormattedValue()
                        txt = backport.text(R.strings.epic_battle.booster.description.bonusValueTime.dyn(booster.boosterGuiType)(), effectValue=goodiesEffectValue, effectTime=goodiesEffectTime)
                        rewards.append(txt)

        return rewards

    def __getDifference(self, quest):
        progress = quest['progressList']
        return progress[0]['progressDiff'] if progress else ''

    def updateQuestsInfo(self, arenaUniqueID):
        self.__arenaUniqueID = arenaUniqueID
        battleResultsVO = self.__battleResults.getResultsVO(self.__arenaUniqueID)['quests']
        if not battleResultsVO:
            return
        progressionQuests = self.__eventProgression.getActiveQuestsAsDict().values()
        battleResultsVOSorted = []
        for br in battleResultsVO:
            questInfo = br['questInfo']
            questID = questInfo['questID']
            for epq in progressionQuests:
                if questID == epq.getID():
                    battleResultsVOSorted.append((epq.getPriority(), br))
                    break

        battleResultsVOSorted.sort(key=lambda q: q[0], reverse=True)
        with self.viewModel.transaction() as model:
            questsArray = Array()
            for _, quest in battleResultsVOSorted:
                questInfo = quest['questInfo']
                questID = questInfo['questID']
                if questID in self.__eventProgression.getActiveQuestIDs():
                    questModel = QuestProgressItemModel()
                    questModel.setId(questID)
                    questModel.setEventType(questInfo['eventType'])
                    questModel.setName(quest['title'])
                    questModel.setDesc(quest['descr'])
                    questModel.setDeltaLabel(self.__getDifference(quest))
                    questModel.setValue(questInfo['currentProgrVal'])
                    questModel.setMaximum(questInfo['maxProgrVal'])
                    currentQuest = findFirst(lambda q: q.getID() == questID, progressionQuests)
                    questModel.setRewards(', '.join(self.__getRewards(currentQuest)))
                    questsArray.addViewModel(questModel)

            model.setQuests(questsArray)

    def _onLoading(self, *args, **kwargs):
        pass


class EpicQuestRewardTooltip(ViewImpl):
    __slots__ = ('__sourceDataModel',)

    def __init__(self, sourceDataModel):
        contentResID = R.views.lobby.epic.tooltips.QuestProgressTooltip()
        settings = ViewSettings(contentResID)
        settings.model = QuestProgressItemModel()
        super(EpicQuestRewardTooltip, self).__init__(settings)
        self.__sourceDataModel = sourceDataModel

    def _finalize(self):
        super(EpicQuestRewardTooltip, self)._finalize()
        self.__sourceDataModel = None
        return

    def _onLoading(self, *args, **kwargs):
        super(EpicQuestRewardTooltip, self)._initialize(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setRewards(self.__sourceDataModel.getRewards())
