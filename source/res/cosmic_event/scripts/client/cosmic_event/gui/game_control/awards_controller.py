# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/game_control/awards_controller.py
import typing
from chat_shared import SYS_MESSAGE_TYPE
from cosmic_event.gui.game_control.progression_controller import QUEST_STEP_REGEX, ACHIEVEMENT_STEP_REGEX
from cosmic_event.gui.gui_constants import SCH_CLIENT_MSG_TYPE, ACHIEVEMENTS_IDS
from cosmic_event.gui.impl.lobby.rewards_view.rewards_view import RewardsWindow
from cosmic_event.skeletons.progression_controller import ICosmicEventProgressionController
from gui.game_control.AwardController import ServiceChannelHandler
from gui.impl.pub.notification_commands import WindowNotificationCommand
from helpers import dependency
from skeletons.gui.impl import INotificationWindowController
from skeletons.gui.system_messages import ISystemMessages
if typing.TYPE_CHECKING:
    from typing import Tuple, List
    from messenger.proto.bw.wrappers import ServiceChannelMessage
    from skeletons.gui.game_control import IAwardController

class CosmicProgressionTokenQuestsHandler(ServiceChannelHandler):
    _notificationMgr = dependency.descriptor(INotificationWindowController)
    _systemMessages = dependency.descriptor(ISystemMessages)
    _cosmicProgression = dependency.descriptor(ICosmicEventProgressionController)

    def __init__(self, awardCtrl):
        super(CosmicProgressionTokenQuestsHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        completedQuestsIDs = [ questID for questID in message.data.get('completedQuestIDs', set()) if QUEST_STEP_REGEX.match(questID) or ACHIEVEMENT_STEP_REGEX.match(questID) ]
        allQuests = self._cosmicProgression.getQuestsForAwardsScreen()
        achievementsWindow = None
        if ACHIEVEMENTS_IDS.issubset(completedQuestsIDs):
            achievementQuests = []
            for questID in ACHIEVEMENTS_IDS:
                achievementQuests.append(allQuests[questID])
                completedQuestsIDs.remove(questID)

            achievementsWindow = RewardsWindow(quests=achievementQuests)
        for questID in completedQuestsIDs:
            progressionQuests = [allQuests[questID]]
            window = RewardsWindow(quests=progressionQuests)
            self._notificationMgr.append(WindowNotificationCommand(window))

        if achievementsWindow is not None:
            self._notificationMgr.append(WindowNotificationCommand(achievementsWindow))
        return

    def _needToShowAward(self, ctx):
        if not super(CosmicProgressionTokenQuestsHandler, self)._needToShowAward(ctx):
            return False
        _, message = ctx
        isCosmicQuest = self._cosmicProgression.isCosmicProgressionQuest
        completedQuestIDs = message.data.get('completedQuestIDs', set())
        return any((isCosmicQuest(questID) for questID in completedQuestIDs))


class CosmicDailyQuestsHandler(ServiceChannelHandler):
    _systemMessages = dependency.descriptor(ISystemMessages)
    _cosmicProgression = dependency.descriptor(ICosmicEventProgressionController)
    _CLIENT_MSG_TYPE = SCH_CLIENT_MSG_TYPE.COSMIC_DAILY

    def __init__(self, awardCtrl):
        super(CosmicDailyQuestsHandler, self).__init__(SYS_MESSAGE_TYPE.cosmicEventBattleResults.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        for questID in message.data.get('detailedRewards', {}):
            if self._cosmicProgression.isCosmicProgressionQuest(questID) and not ACHIEVEMENT_STEP_REGEX.match(questID):
                self._systemMessages.proto.serviceChannel.pushClientMessage({'rewards': message.data['detailedRewards'][questID]}, self._CLIENT_MSG_TYPE)

    def _needToShowAward(self, ctx):
        if not super(CosmicDailyQuestsHandler, self)._needToShowAward(ctx):
            return False
        _, message = ctx
        completedQuestIDs = message.data.get('completedQuestIDs', set())
        return any((questID for questID in completedQuestIDs if self._cosmicProgression.isCosmicProgressionQuest(questID)))
