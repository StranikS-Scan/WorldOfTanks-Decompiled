# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/game_control/awards_controller.py
import logging
import types
from chat_shared import SYS_MESSAGE_TYPE
from gui import SystemMessages
from gui.game_control.AwardController import MultiTypeServiceChannelHandler, PunishWindowHandler
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from optional_bonuses import BONUS_MERGERS
from skeletons.gui.system_messages import ISystemMessages
from white_tiger.gui.shared.event_dispatcher import showWtEventAwardWindow
from white_tiger.gui.white_tiger_gui_constants import PROGRESSION_COMPLETE_TOKEN
from white_tiger.gui.wt_event_helpers import isWTEventProgressionQuest, isWtEventSpecialQuest
from white_tiger.skeletons.economics_controller import IEconomicsController
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
_logger = logging.getLogger(__name__)

class WhiteTigerQuestsHandler(MultiTypeServiceChannelHandler):
    __systemMessages = dependency.descriptor(ISystemMessages)
    __economicsCtrl = dependency.descriptor(IEconomicsController)
    __wtCtrl = dependency.descriptor(IWhiteTigerController)
    __STR_RES = R.strings.white_tiger_lobby.notifications.progression

    def __init__(self, awardCtrl):
        handlers = {SYS_MESSAGE_TYPE.tokenQuests.index(), SYS_MESSAGE_TYPE.wtBattleResults.index()}
        super(WhiteTigerQuestsHandler, self).__init__(handlers, awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        completedQuestIds = message.data.get('completedQuestIDs', set())
        lastQuestId = self.__economicsCtrl.getLastProgressionStepID()
        completedQuestIds = [ (self.__getStageIdx(questId), questId) for questId in completedQuestIds if isWTEventProgressionQuest(questId) ]
        completedQuestIds.sort()
        for stageIdx, questId in completedQuestIds:
            rewardData = {}
            additionalRewards = {}
            hasCompletedProgression = questId == lastQuestId
            if isWTEventProgressionQuest(questId):
                self.__showStageCompletedMessage(questId, stageIdx, hasCompletedProgression)
                mainRewards, secondaryRewards = self.__economicsCtrl.getProgressionPrioritisedRewards(questId)
                self.__updateReward(rewardData, mainRewards)
                self.__updateReward(additionalRewards, secondaryRewards)
            if rewardData or additionalRewards:
                showWtEventAwardWindow(rewardData, additionalRewards, hasCompletedProgression)

    def _needToShowAward(self, ctx):
        if not super(WhiteTigerQuestsHandler, self)._needToShowAward(ctx):
            return False
        else:
            _, message = ctx
            if message is None or not message.data or not isinstance(message.data, types.DictType):
                return False
            completedQuests = message.data.get('completedQuestIDs', None)
            return completedQuests and self.__hasWTEventQuest(completedQuests)

    def __hasWTEventQuest(self, completedQuestIDs):
        for questId in completedQuestIDs:
            if isWTEventProgressionQuest(questId) or isWtEventSpecialQuest(questId):
                return True

        return False

    def __updateReward(self, rewardData, newRewardData):
        for rewardKey, rewardValue in newRewardData.items():
            if rewardKey in BONUS_MERGERS.keys():
                BONUS_MERGERS[rewardKey](rewardData, rewardKey, rewardValue, False, 1, None)
            if rewardKey == 'lootBox' and isinstance(rewardValue, dict):
                for name, data in rewardValue.items():
                    count = rewardData.setdefault(rewardKey, {}).setdefault(name, {'count': 0})
                    count['count'] = count['count'] + data.get('count', 0)

            if rewardKey == 'ticket' and isinstance(rewardValue, dict):
                BONUS_MERGERS['tokens'](rewardData, rewardKey, rewardValue, False, 1, None)
            if PROGRESSION_COMPLETE_TOKEN in rewardValue:
                continue
            _logger.warning('Unknown reward in award screen. key: %s, value: %s', rewardKey, rewardValue)

        return

    def __showStageCompletedMessage(self, questId, stageIdx, hasCompletedProgression):
        rewards = self.__getRewards(questId)
        if hasCompletedProgression:
            SystemMessages.pushMessage(text=backport.text(self.__STR_RES.completed(), rewards=rewards), type=SystemMessages.SM_TYPE.WTEventProgression, priority=NotificationPriorityLevel.HIGH)
        else:
            SystemMessages.pushMessage(text=backport.text(self.__STR_RES.stageAchieved(), stageIdx=str(stageIdx + 1), rewards=rewards), type=SystemMessages.SM_TYPE.WTEventProgression, priority=NotificationPriorityLevel.MEDIUM)

    def __getStageIdx(self, questID):
        progression = self.__economicsCtrl.getConfig()['progression']
        for idx, stage in enumerate(progression):
            if questID == stage['quest']:
                return idx

    def __getRewards(self, questID):
        rewards = self.__economicsCtrl.getProgressionRewards(questID)
        formattedList = [ formatted for r in rewards for formatted in r.formattedList() ]
        return ', '.join(formattedList)


class WhiteTigerPunishHandler(PunishWindowHandler):

    @property
    def channelType(self):
        return SYS_MESSAGE_TYPE.wtBattleResults.index()
