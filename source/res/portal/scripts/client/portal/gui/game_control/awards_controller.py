# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/game_control/awards_controller.py
import sys
from Queue import PriorityQueue
from enum import IntEnum
from wotdecorators import singleton
from chat_shared import SYS_MESSAGE_TYPE
from helpers import dependency
from gui.game_control.AwardController import ServiceChannelHandler
from portal.gui.portal_event_helpers import isPortalProgressionQuest, PROGRESSION_QUEST_PREFIX, isPortalLastLevelQuest, isPortalAllVehicleUpgradesQuest
from portal.gui.shared.event_dispatcher import showAwardsView
from portal.messenger.formatters.portal_formatters import PortalQuestAchievesFormatter
from portal.skeletons.portal_event_controller import IPortalEventController
from skeletons.gui.server_events import IEventsCache

@singleton
class _AwardViewQueue(object):

    def __init__(self):
        self.__viewQueue = PriorityQueue()
        self.__hasActiveView = False
        self.__currentCallback = None
        return

    def show(self, priority, rewardsData, callback=None):
        if self.__hasActiveView:
            self.__viewQueue.put((priority, rewardsData, callback))
        else:
            self.__showAwardsView(rewardsData, callback)

    def close(self):
        if self.__currentCallback:
            self.__currentCallback()
            self.__currentCallback = None
        if self.__viewQueue.empty():
            self.__hasActiveView = False
            return
        else:
            _, awardsData, callback = self.__viewQueue.get()
            self.__showAwardsView(awardsData, callback)
            return

    def __showAwardsView(self, rewardsData, callback):
        self.__hasActiveView = True
        self.__currentCallback = callback
        showAwardsView(rewardsData, self.close)


class AwardType(IntEnum):
    PROGRESSION = 0
    LAST_LEVEL_VICTORY = 1
    ALL_VEHICLES_UPGRADED = 2


class PortalProgressionAwardHandler(ServiceChannelHandler):
    __portalController = dependency.descriptor(IPortalEventController)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, awardsController):
        super(PortalProgressionAwardHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardsController)
        self._achievesFormatter = PortalQuestAchievesFormatter()

    def _showAward(self, ctx):
        data = ctx[1].data
        for questID in data.get('completedQuestIDs', set()):
            formattedRewards = self._achievesFormatter.formatQuestAchieves(data.get('detailedRewards', {}).get(questID, {}), asBattleFormatter=False)
            if isPortalProgressionQuest(questID):
                self.__showProgressionAward(questID, data, formattedRewards)
            if isPortalLastLevelQuest(questID):
                self.__showLastLevelVictoryAward(questID, data, formattedRewards)
            if isPortalAllVehicleUpgradesQuest(questID):
                self.__showAllVehiclesUpgraded(questID, data, formattedRewards)

    def __showProgressionAward(self, questID, data, formattedRewards):
        stage = int(questID[len(PROGRESSION_QUEST_PREFIX):])
        rewardsData = {'type': AwardType.PROGRESSION,
         'stage': stage,
         'rewards': data.get('detailedRewards', {}).get(questID, {})}
        _AwardViewQueue.show(stage, rewardsData)

    def __getRewards(self, questID):
        quests = self.__eventsCache.getAllQuests(lambda quest: quest.getID() == questID)
        bonuses = quests[questID].getBonuses()
        formattedList = []
        for reward in bonuses:
            for item in reward.formattedList():
                formattedList.append(item)

        return '{0}'.format('\n'.join(formattedList))

    def __showLastLevelVictoryAward(self, questID, data, formattedRewards):
        rewardsData = {'type': AwardType.LAST_LEVEL_VICTORY,
         'rewards': data.get('detailedRewards', {}).get(questID, {})}
        _AwardViewQueue.show(sys.maxint, rewardsData, self.__portalController.showOutroVideo)

    def __showAllVehiclesUpgraded(self, questID, data, formattedRewards):
        rewardsData = {'type': AwardType.ALL_VEHICLES_UPGRADED,
         'rewards': data.get('detailedRewards', {}).get(questID, {})}
        _AwardViewQueue.show(sys.maxint, rewardsData)
