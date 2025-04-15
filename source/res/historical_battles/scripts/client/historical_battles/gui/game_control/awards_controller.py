# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/game_control/awards_controller.py
import sys
from Queue import PriorityQueue
import HBAccountSettings
from wotdecorators import singleton
from historical_battles.gui.gui_constants import SM_TYPE_HB_PROGRESSION
from historical_battles.gui.shared.event_dispatcher import showAwardsView
from chat_shared import SYS_MESSAGE_TYPE
from gui.game_control.AwardController import ServiceChannelHandler
from helpers import dependency
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from historical_battles_common.hb_constants import AccountSettingsKeys
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


class HBLastAwardHandler(ServiceChannelHandler):
    __notificationsCtrl = dependency.descriptor(IHBEventNotifications)
    QUEST_ID = 'hbMainTankmanPrize'

    def __init__(self, awardCtrl):
        super(HBLastAwardHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    def _showAward(self, ctx):
        data = ctx[1].data
        for qID in data.get('completedQuestIDs', set()):
            if qID == self.QUEST_ID:
                AwardViewer.show({'finishStage': True,
                 'stage': sys.maxint,
                 'frontId': HBAccountSettings.getSettings(AccountSettingsKeys.LAST_FRONT_ID_IN_AWARDS),
                 'detailedRewards': data.get('detailedRewards', {}).get(self.QUEST_ID, {}),
                 'showAwardWindow': True,
                 'isSpecial': True})
                self.__notificationsCtrl.pushLastAwardMessage(data)
