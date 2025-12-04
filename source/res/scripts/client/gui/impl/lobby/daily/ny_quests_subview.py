# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/daily/ny_quests_subview.py
import logging
import weakref
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.daily.ny_quests_view_model import NyQuestsViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.pub import ViewImpl
from gui.impl.backport.backport_tooltip import _BackportTooltipContent
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.shared.missions.packers.events import getEventUIDataPacker
from gui.impl.lobby.daily.daily_helpers import modifyPostbattleConditions, modifyTokenQuestConditions
from gui.impl.gen.view_models.common.missions.event_model import EventStatus
from new_year.gui.impl.lobby.new_year.quests.ny_quest_helper import getCurrentWeek
from new_year.gui.game_control.ny_controller import getNYQuests
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from new_year.gui.impl.new_year.new_year_bonus_packer import getNewYearBonusPacker
from new_year_account_settings import getNYSetting, setNYSettings
from gui.shared.event_dispatcher import showNyDailyQuestsInfoWindow
from new_year.ny_constants import NY_IS_QUESTS_INTRO_SHOWED, NY_SEEN_QUESTS
from new_year.skeletons.new_year import INewYearController
from skeletons.gui.game_control import IUnseenEventsCounter
from gui.server_events.event_items import TokenQuest
_logger = logging.getLogger(__name__)
_CURRENT_TAB_IDX = 3
INT_MAX_VALUE = 2147483647L

class NySubViewBase(ViewImpl):

    def activate(self):
        self._subscribe()
        self._update()

    def deactivate(self):
        self._unsubscribe()

    def _update(self):
        raise NotImplementedError


class NyQuestsSubView(NySubViewBase):
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    __nyCtrl = dependency.descriptor(INewYearController)
    __unseenEventsManager = dependency.descriptor(IUnseenEventsCounter)
    __slots__ = ('__parent', '__tooltipData', '__subviewTabIdx', '__currentTabIdx', '__minLevel', '__maxLevel', '__dailyQuests', '__weeklyQuests')

    def __init__(self, parent, layoutID):
        viewSettings = ViewSettings(layoutID, ViewFlags.VIEW, NyQuestsViewModel())
        super(NyQuestsSubView, self).__init__(viewSettings)
        self.__parent = weakref.proxy(parent)
        self.__tooltipData = {}
        self.__subviewTabIdx = 0
        self.__minLevel = MAX_VEHICLE_LEVEL
        self.__maxLevel = MIN_VEHICLE_LEVEL
        self.__dailyQuests, self.__weeklyQuests = getNYQuests(self.eventsCache)

    @property
    def viewModel(self):
        return super(NyQuestsSubView, self).getViewModel()

    @property
    def currentTabIdx(self):
        return self.__parent.getCurrentTabID()

    @property
    def tooltipData(self):
        return self.__tooltipData

    def _getEvents(self):
        return ((self.viewModel.onTypeSelect, self.__onTypeSelect), (self.__nyCtrl.onStateChanged, self.__updateNYState))

    def activate(self):
        super(NyQuestsSubView, self).activate()
        if not getNYSetting(NY_IS_QUESTS_INTRO_SHOWED):
            showNyDailyQuestsInfoWindow()
            setNYSettings(NY_IS_QUESTS_INTRO_SHOWED, True)

    def deactivate(self):
        super(NyQuestsSubView, self).deactivate()
        self.__subviewTabIdx = 0
        self.__tooltipData = {}

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            if tooltipData is not None:
                return _BackportTooltipContent(tooltipData)
            return
        elif contentID == R.views.gui_lootboxes.lobby.gui_lootboxes.tooltips.LootboxTooltip():
            tooltipData = self.__getBackportTooltipData(event)
            lootBoxIdStr = tooltipData.specialArgs[0].getID()
            lootBox = self.itemsCache.items.tokens.getLootBoxByID(int(lootBoxIdStr))
            return LootboxTooltip(lootBox)
        else:
            return

    def __getBackportTooltipData(self, event):
        missionParam = event.getArgument('tooltipId', '')
        missionParams = missionParam.rsplit(':', 1)
        if len(missionParams) != 2:
            return self.__tooltipData.get(missionParam)
        missionId, tooltipId = missionParams
        tooltipsData = self.__tooltipData.get(missionId, {})
        tooltipData = tooltipsData.get(tooltipId)
        return tooltipData

    def _update(self):
        with self.viewModel.transaction() as vm:
            vm.setCurrentTabIdx(_CURRENT_TAB_IDX)
            self.__updateQuests(vm.getQuests())
            self.__updateQuestsCountdown(vm)
            self.__updateLevels(vm)
            self.__updateCelebText(vm)

    def __updateNYState(self):
        if not self.__nyCtrl.isEnabled():
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), EVENT_BUS_SCOPE.LOBBY)

    def __updateQuests(self, questsInModelToUpdate):
        questsInModelToUpdate.clear()
        quests = self.__dailyQuests if self.__subviewTabIdx == 0 else self.__weeklyQuests
        seenQuests = getNYSetting(NY_SEEN_QUESTS)
        for questID, quest in sorted(quests.iteritems(), key=lambda (_, q): not isinstance(q, TokenQuest)):
            questVehDescr = quest.vehicleReqs.getConditions().find('vehicleDescr')
            if questVehDescr is not None:
                levels = questVehDescr.getData()['levels'][0][1]
                minLevel = min(levels)
                maxLevel = max(levels)
                self.__minLevel = minLevel if self.__minLevel > minLevel else self.__minLevel
                self.__maxLevel = maxLevel if self.__maxLevel < maxLevel else self.__maxLevel
            packer = getEventUIDataPacker(quest, bonusPackerGetter=getNewYearBonusPacker)
            questModel = packer.pack()
            questModel.setIsFirstView(not self.__isQuestsSeen(questID, seenQuests))
            self.__tooltipData[questID] = packer.getTooltipData()
            if questVehDescr is None:
                modifyTokenQuestConditions(quest, questModel)
            else:
                modifyPostbattleConditions(quest, questModel)
            questsInModelToUpdate.addViewModel(questModel)
            if quest.isCompleted():
                questModel.setStatus(EventStatus.DONE)
            else:
                questModel.setStatus(EventStatus.ACTIVE)
            self.eventsCache.questsProgress.markQuestProgressAsViewed(questID)

        setNYSettings(NY_SEEN_QUESTS, seenQuests)
        self.__updateSeenQuests(seenQuests)
        questsInModelToUpdate.invalidate()
        return

    def __updateSeenQuests(self, seenQuests):
        for questID in seenQuests:
            self.__unseenEventsManager.seenEvent(questID, 1)

    def __isQuestsSeen(self, questID, seenQuests):
        if questID in seenQuests:
            return True
        seenQuests.append(questID)
        return False

    def __updateQuestsCountdown(self, model):
        questItems = self.__dailyQuests.items() if self.__subviewTabIdx == 0 else self.__weeklyQuests.items()
        resetDelta = self.__extractResetTime(questItems)
        model.setCountDown(int(resetDelta))

    def __extractResetTime(self, questItems):
        result = INT_MAX_VALUE
        for _, quest in questItems:
            result = min(result, quest.getFinishTimeLeft())

        return result

    def __updateLevels(self, model):
        model.setMinLevel(self.__minLevel)
        model.setMaxLevel(self.__maxLevel)

    @staticmethod
    def __updateCelebText(model):
        model.setPersonTextNumber(getCurrentWeek())

    @args2params(int)
    def __onTypeSelect(self, typeId):
        if typeId is not None:
            self.__subviewTabIdx = int(typeId)
            self._update()
        return
