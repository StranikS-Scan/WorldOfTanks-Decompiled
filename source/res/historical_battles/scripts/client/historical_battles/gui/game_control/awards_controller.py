# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/game_control/awards_controller.py
import sys
from account_shared import getFairPlayViolationName
from chat_shared import SYS_MESSAGE_TYPE
from debug_utils import LOG_WARNING
from gui.game_control.AwardController import ServiceChannelHandler
from helpers import dependency
from Queue import PriorityQueue
from wotdecorators import singleton
from historical_battles_common.hb_constants_extension import ARENA_BONUS_TYPE
from historical_battles_common.hb_constants import HB_VIOLATIONS
from historical_battles.gui.gui_constants import SM_TYPE_HB_PROGRESSION, SCH_CLIENT_MSG_TYPE
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_quest_awards_model import AwardsViewType
from historical_battles.gui.server_events.battle_quests.quests_container import getHBQuestsContainer
from historical_battles.gui.shared.event_dispatcher import showAwardsView, showHBFairplayDialog, showHBFairplayWarningDialog
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.skeletons.gui.hb_notifications_controller import IHBEventNotifications

@singleton
class AwardViewer(object):

    def __init__(self):
        self.__viewQueue = PriorityQueue()
        self.__isViewed = False

    def show(self, stage):
        if self.__isViewed:
            self.__viewQueue.put((stage['stage'], stage))
        else:
            self.__isViewed = True
            showAwardsView(stage, self.close)

    def close(self):
        if self.__viewQueue.empty():
            self.__isViewed = False
            return
        _, stage = self.__viewQueue.get()
        showAwardsView(stage, self.close)


class HBProgressionStageHandler(ServiceChannelHandler):
    __notificationsCtrl = dependency.descriptor(IHBEventNotifications)
    __gameEventController = dependency.descriptor(IGameEventController)
    __hbProgressionController = dependency.descriptor(IHBProgressionOnTokensController)

    def __init__(self, awardCtrl):
        super(HBProgressionStageHandler, self).__init__(SYS_MESSAGE_TYPE.__getattr__(SM_TYPE_HB_PROGRESSION).index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        for stage in message.data.get('stages', set()):
            if stage.get('showAwardWindow', False):
                AwardViewer.show(stage)

        self.__notificationsCtrl.pushRegularAwardMessage(message)


class HBQuestsAwardHandler(ServiceChannelHandler):
    __notificationsCtrl = dependency.descriptor(IHBEventNotifications)
    __QUEST_PREFIX = 'hb26'

    def __init__(self, awardCtrl):
        super(HBQuestsAwardHandler, self).__init__(SYS_MESSAGE_TYPE.hbBattleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        serviceMsg = ctx[1]
        data = serviceMsg.data
        completedQuestIDs = data.get('completedQuestIDs', set())
        if not any((qID.startswith(self.__QUEST_PREFIX) for qID in completedQuestIDs)):
            return
        container = getHBQuestsContainer()
        allowedQuests = {qID:quest for qID, quest in container.getQuests()}
        targetQuests = completedQuestIDs.intersection(allowedQuests.keys())
        if not targetQuests:
            return
        self.__notificationsCtrl.pushBattleQuestAwardMessage(serviceMsg)
        detailedRewards = data.get('detailedRewards', {})
        frontId = data.get('frontID', 0)
        for qID in targetQuests:
            if container.isDailyQuest(allowedQuests[qID]):
                continue
            questRewards = detailedRewards.get(qID)
            if questRewards:
                AwardViewer.show({'stage': sys.maxint,
                 'viewType': AwardsViewType.QUESTS,
                 'finishStage': True,
                 'frontId': frontId,
                 'detailedRewards': questRewards})


class HBFairplayHandler(ServiceChannelHandler):
    __notificationsCtrl = dependency.descriptor(IHBEventNotifications)
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, awardCtrl):
        super(HBFairplayHandler, self).__init__(SYS_MESSAGE_TYPE.hbBattleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        bonusType = message.data.get('bonusType')
        if bonusType not in ARENA_BONUS_TYPE.HB_RANGE:
            return
        else:
            fairplayViolations = message.data.get('fairplayViolations', None)
            penaltyType = None
            violation = None
            if fairplayViolations[1] != 0:
                penaltyType = 'penalty'
                violation = fairplayViolations[1]
            elif fairplayViolations[0] != 0:
                penaltyType = 'warning'
                violation = fairplayViolations[0]
            else:
                return
            violationName = getFairPlayViolationName(violation)
            if violationName not in HB_VIOLATIONS:
                LOG_WARNING('Unknown violation in historical battles', violationName)
                return
            banDuration = message.data['restriction'][1] if 'restriction' in message.data else None
            banExpiryTime = self.__gameEventController.banExpiryTime
            data = {'isStarted': banExpiryTime is not None,
             'reason': violationName,
             'banExpiryTime': banExpiryTime}
            if penaltyType == 'penalty':
                if banDuration > 0:
                    showHBFairplayDialog(data)
                else:
                    showHBFairplayWarningDialog(violationName)
                    self.__notificationsCtrl.pushArenaPunishmentSysMsg(data, SCH_CLIENT_MSG_TYPE.HB_ARENA_WARNING_NOTIFICATIONS)
            elif penaltyType == 'warning':
                showHBFairplayWarningDialog(violationName)
                self.__notificationsCtrl.pushArenaPunishmentSysMsg(data, SCH_CLIENT_MSG_TYPE.HB_ARENA_WARNING_NOTIFICATIONS)
            return
