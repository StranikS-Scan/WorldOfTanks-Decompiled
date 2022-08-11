# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/wot_anniversary/__init__.py
from gui.server_events.events_helpers import EventInfoModel
from gui.wot_anniversary.wot_anniversary_helpers import findWeeklyQuest, WOT_ANNIVERSARY_DAILY_QUEST_PREFIX, WOT_ANNIVERSARY_WEEKLY_QUEST_PREFIX, WOT_ANNIVERSARY_QUEST_POINTS, WOT_ANNIVERSARY_FINAL_REWARD_PREFIX, WOT_ANNIVERSARY_FIRST_FINAL_REWARD_QUEST, WOT_ANNIVERSARY_SECOND_FINAL_REWARD_QUEST, getQuestNeededTokensCount, WOT_ANNIVERSARY_LAST_WEEKLY_QUEST
from helpers import dependency
from helpers import time_utils
from skeletons.gui.game_control import IWotAnniversaryController
from web.web_client_api import w2capi, w2c, W2CSchema
from web.web_client_api.quests import questAsDict
from wot_anniversary_common import WotAnniversaryUrls

@w2capi(name='wot_anniversary', key='action')
class WotAnniversaryWebApi(object):
    __wotAnniversaryCtrl = dependency.descriptor(IWotAnniversaryController)

    @w2c(W2CSchema, 'get_settings')
    def getSettings(self, _):
        quests = self.__wotAnniversaryCtrl.getQuests()
        result = {'infoPageUrl': self.__wotAnniversaryCtrl.getUrl(WotAnniversaryUrls.INFO_PAGE),
         'shopEventPath': self.__wotAnniversaryCtrl.getUrl(WotAnniversaryUrls.SHOP_EVENT_PATH),
         'eventStartTimestamp': self.__wotAnniversaryCtrl.getConfig().startTime,
         'eventEndTimestamp': self.__wotAnniversaryCtrl.getConfig().endTime,
         'bigQuestPeriod': self.__wotAnniversaryCtrl.getConfig().bigQuestPeriod,
         'quests': {'daily': {'questIdPrefix': WOT_ANNIVERSARY_DAILY_QUEST_PREFIX},
                    'big': {'questIdPrefix': WOT_ANNIVERSARY_WEEKLY_QUEST_PREFIX},
                    'reward1': {'questId': WOT_ANNIVERSARY_FIRST_FINAL_REWARD_QUEST},
                    'reward2': {'questId': WOT_ANNIVERSARY_SECOND_FINAL_REWARD_QUEST}},
         'rewards': {'token': WOT_ANNIVERSARY_QUEST_POINTS,
                     'reward1': {'maxPoints': getQuestNeededTokensCount(quests.get(WOT_ANNIVERSARY_FIRST_FINAL_REWARD_QUEST))},
                     'reward2': {'maxPoints': getQuestNeededTokensCount(quests.get(WOT_ANNIVERSARY_SECOND_FINAL_REWARD_QUEST))}}}
        return result

    @w2c(W2CSchema, 'get_time_data')
    def getTimeData(self, _):
        isNotLastDay = not self.__wotAnniversaryCtrl.isLastDayNow()
        nextGameDay = time_utils.getCurrentLocalServerTimestamp() + EventInfoModel.getDailyProgressResetTimeDelta()
        quests = self.__wotAnniversaryCtrl.getQuests()
        _, weeklyQuest = findWeeklyQuest(quests)
        endTimeOfWeekly = None
        if weeklyQuest is not None and weeklyQuest.getID() != WOT_ANNIVERSARY_LAST_WEEKLY_QUEST:
            endTimeOfWeekly = weeklyQuest.getFinishTime() + time_utils.ONE_MINUTE
        return {'endTimeOfDaily': nextGameDay + time_utils.ONE_MINUTE if isNotLastDay else None,
         'endTimeOfBig': endTimeOfWeekly}

    @w2c(W2CSchema, 'get_quests')
    def getQuests(self, _):
        data = {}
        quests = self.__wotAnniversaryCtrl.getQuests()
        dailyQuestName = self.__wotAnniversaryCtrl.getDailyQuestName()
        dQuest = quests.get(dailyQuestName)
        if dQuest is not None:
            data[dailyQuestName] = questAsDict(dQuest)
        weeklyQuestID, wQuest = findWeeklyQuest(quests)
        if wQuest is not None:
            data[weeklyQuestID] = questAsDict(wQuest)
        for qID, quest in quests.iteritems():
            if qID.startswith(WOT_ANNIVERSARY_FINAL_REWARD_PREFIX):
                data[qID] = questAsDict(quest)

        return data
