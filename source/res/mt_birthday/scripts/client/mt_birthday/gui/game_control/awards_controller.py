# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/game_control/awards_controller.py
import typing
from chat_shared import SYS_MESSAGE_TYPE
from gui.game_control.AwardController import ServiceChannelHandler
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.server_events.bonuses import getNonQuestBonuses
from helpers import dependency
from mt_birthday.gui.game_control import TanksBirthdayController
from mt_birthday.gui.impl.lobby.birthday.birthday_rewards_view import BirthdayRewardsViewWindow
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from mt_birthday_common.constants import MT_BIRTHDAY_QUEST_PROGRESSION_ID, MT_BIRTHDAY_WELCOME_QUEST_ID, MT_BIRTHDAY_BADGE_QUEST_PROGRESSION_ID
from skeletons.gui.impl import INotificationWindowController
if typing.TYPE_CHECKING:
    from typing import Tuple, List
    from messenger.proto.bw.wrappers import ServiceChannelMessage
    from skeletons.gui.game_control import IAwardController

def _getBonuses(rewards):
    bonuses = []
    for key, value in rewards.items():
        bonus = getNonQuestBonuses(key, value)
        if bonus:
            bonuses.extend(bonus)

    return bonuses


class BirthdayProgressionTokenQuestsHandler(ServiceChannelHandler):
    _notificationMgr = dependency.descriptor(INotificationWindowController)
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)

    def __init__(self, awardCtrl):
        super(BirthdayProgressionTokenQuestsHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        completedQuestsIDs = [ questID for questID in message.data.get('completedQuestIDs', set()) if questID.startswith(MT_BIRTHDAY_QUEST_PROGRESSION_ID) ]
        allQuests = self.__tankBirthdayController.progression.progressionConfig
        for questID in completedQuestsIDs[::-1]:
            rewards = message.data.get('detailedRewards', {}).get(questID)
            level = int(questID.split('_')[-1])
            progressQuest = allQuests[level]
            isInfinity = progressQuest['isInfinity']
            bonuses = _getBonuses(rewards)
            window = BirthdayRewardsViewWindow(bonuses, '', level, isFinalReward=isInfinity)
            self._notificationMgr.append(WindowNotificationCommand(window))

    def _needToShowAward(self, ctx):
        _, message = ctx
        if not super(BirthdayProgressionTokenQuestsHandler, self)._needToShowAward(ctx):
            return False
        _, message = ctx
        isBirthdayProgressionQuest = self.__tankBirthdayController.progression.isBirthdayProgressionQuest
        completedQuestIDs = message.data.get('completedQuestIDs', set())
        return any((isBirthdayProgressionQuest(questID) for questID in completedQuestIDs))


class BirthdayProgressionBadgeTokenQuestsHandler(ServiceChannelHandler):
    _notificationMgr = dependency.descriptor(INotificationWindowController)

    def __init__(self, awardCtrl):
        super(BirthdayProgressionBadgeTokenQuestsHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        completedQuestsIDs = [ questID for questID in message.data.get('completedQuestIDs', set()) if questID.startswith(MT_BIRTHDAY_BADGE_QUEST_PROGRESSION_ID) ]
        for questID in completedQuestsIDs:
            rewards = message.data.get('detailedRewards', {}).get(questID)
            bonuses = _getBonuses(rewards)
            window = BirthdayRewardsViewWindow(bonuses, '', 17, isFinalReward=True)
            self._notificationMgr.append(WindowNotificationCommand(window))

    def _needToShowAward(self, ctx):
        _, message = ctx
        if not super(BirthdayProgressionBadgeTokenQuestsHandler, self)._needToShowAward(ctx):
            return False
        _, message = ctx
        completedQuestIDs = message.data.get('completedQuestIDs', set())
        return any((questID for questID in completedQuestIDs if questID == MT_BIRTHDAY_BADGE_QUEST_PROGRESSION_ID))


class BirthdayWelcomeTokenQuestsHandler(ServiceChannelHandler):
    _notificationMgr = dependency.descriptor(INotificationWindowController)
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)

    def __init__(self, awardCtrl):
        super(BirthdayWelcomeTokenQuestsHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        rewards = message.data.get('detailedRewards', {}).get(MT_BIRTHDAY_WELCOME_QUEST_ID)
        bonuses = _getBonuses(rewards)
        window = BirthdayRewardsViewWindow(bonuses, '', 0, isRewardSeen=False, isFinalReward=False)
        self._notificationMgr.append(WindowNotificationCommand(window))

    def _needToShowAward(self, ctx):
        _, message = ctx
        if not super(BirthdayWelcomeTokenQuestsHandler, self)._needToShowAward(ctx):
            return False
        _, message = ctx
        return MT_BIRTHDAY_WELCOME_QUEST_ID in message.data.get('completedQuestIDs', set())
