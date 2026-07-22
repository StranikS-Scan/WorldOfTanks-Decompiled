# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/game_control/awards_controller.py
import typing
import copy
from chat_shared import SYS_MESSAGE_TYPE
from gui.game_control.AwardController import ServiceChannelHandler, MultiTypeServiceChannelHandler
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.server_events.bonuses import getNonQuestBonuses
from helpers import dependency
from mt_birthday.gui.impl.lobby.birthday.birthday_rewards_view import BirthdayRewardsViewWindow
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from mt_birthday_common.constants import MT_BIRTHDAY_QUEST_PROGRESSION_ID, MT_BIRTHDAY_WELCOME_QUEST_ID, BIRTHDAY_BADGE_QUEST, BIRTHDAY_CHALLENGE_COMPLETE_QUEST
from optional_bonuses import BONUS_MERGERS
from skeletons.gui.impl import INotificationWindowController
if typing.TYPE_CHECKING:
    from typing import Tuple, List
    from messenger.proto.bw.wrappers import ServiceChannelMessage
    from skeletons.gui.game_control import IAwardController
    from mt_birthday.gui.game_control import TanksBirthdayController

def _getBonuses(rewards):
    bonuses = []
    for key, value in rewards.items():
        bonus = getNonQuestBonuses(key, value)
        if bonus:
            bonuses.extend(bonus)

    return bonuses


class BirthdayProgressionAndBadgeTokenQuestsHandler(ServiceChannelHandler):
    _notificationMgr = dependency.descriptor(INotificationWindowController)
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)

    def __init__(self, awardCtrl):
        super(BirthdayProgressionAndBadgeTokenQuestsHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    @staticmethod
    def getMergedBonusesFromDicts(rewards, rewardsSecond):
        result = copy.deepcopy(rewards)
        for bonusName, bonusValue in rewardsSecond.iteritems():
            if bonusName in BONUS_MERGERS:
                BONUS_MERGERS[bonusName](result, bonusName, bonusValue, False, 1, None)

        return result

    def _showAward(self, ctx):
        hasBadge = False
        _, message = ctx
        completedQuestsIDs = [ questID for questID in message.data.get('completedQuestIDs', set()) if questID.startswith(MT_BIRTHDAY_QUEST_PROGRESSION_ID) or questID == BIRTHDAY_BADGE_QUEST ]
        if BIRTHDAY_BADGE_QUEST in completedQuestsIDs:
            completedQuestsIDs.remove(BIRTHDAY_BADGE_QUEST)
            hasBadge = True
        sortedQuestIDs = sorted(completedQuestsIDs, key=lambda x: int(x.split(MT_BIRTHDAY_QUEST_PROGRESSION_ID + '_')[-1]))
        allQuests = self.__tankBirthdayController.progression.progressionConfig
        for questID in sortedQuestIDs:
            if hasBadge:
                rewards = self.getMergedBonusesFromDicts(message.data.get('detailedRewards', {}).get(questID), message.data.get('detailedRewards', {}).get(BIRTHDAY_BADGE_QUEST))
                hasBadge = False
            else:
                rewards = message.data.get('detailedRewards', {}).get(questID)
            level = int(questID.split('_')[-1])
            progressQuest = allQuests[level]
            isInfinity = progressQuest['isInfinity']
            bonuses = _getBonuses(rewards)
            window = BirthdayRewardsViewWindow(bonuses, '', level, isFinalReward=isInfinity)
            self._notificationMgr.append(WindowNotificationCommand(window))

        if not sortedQuestIDs:
            replyGiftsCount = self.__tankBirthdayController.getBadgeQuestRequiredReplyTokens()
            rewards = message.data.get('detailedRewards', {}).get(BIRTHDAY_BADGE_QUEST)
            bonuses = _getBonuses(rewards)
            window = BirthdayRewardsViewWindow(bonuses, '', 0, isFinalReward=False, isOnlyBadge=True, replyGiftsCount=replyGiftsCount)
            self._notificationMgr.append(WindowNotificationCommand(window))

    def _needToShowAward(self, ctx):
        _, message = ctx
        if not super(BirthdayProgressionAndBadgeTokenQuestsHandler, self)._needToShowAward(ctx):
            return False
        _, message = ctx
        isBirthdayProgressionQuest = self.__tankBirthdayController.progression.isBirthdayProgressionQuest
        completedQuestIDs = message.data.get('completedQuestIDs', set())
        return any((isBirthdayProgressionQuest(questID) or questID.startswith(BIRTHDAY_BADGE_QUEST) for questID in completedQuestIDs))


class BirthdayChallengeTokenQuestsHandler(ServiceChannelHandler):
    _notificationMgr = dependency.descriptor(INotificationWindowController)

    def __init__(self, awardCtrl):
        super(BirthdayChallengeTokenQuestsHandler, self).__init__(SYS_MESSAGE_TYPE.tokenQuests.index(), awardCtrl)

    def _showAward(self, ctx):
        _, message = ctx
        rewards = message.data.get('detailedRewards', {}).get(BIRTHDAY_CHALLENGE_COMPLETE_QUEST)
        bonuses = _getBonuses(rewards)
        window = BirthdayRewardsViewWindow(bonuses, '', 0, isFinalReward=False, isAllChallengesComplete=True)
        self._notificationMgr.append(WindowNotificationCommand(window))

    def _needToShowAward(self, ctx):
        _, message = ctx
        if not super(BirthdayChallengeTokenQuestsHandler, self)._needToShowAward(ctx):
            return False
        _, message = ctx
        return BIRTHDAY_CHALLENGE_COMPLETE_QUEST in message.data.get('completedQuestIDs', set())


class BirthdayWelcomeTokenQuestsHandler(MultiTypeServiceChannelHandler):
    _notificationMgr = dependency.descriptor(INotificationWindowController)
    __tankBirthdayController = dependency.descriptor(ITanksBirthdayController)

    def __init__(self, awardCtrl):
        super(BirthdayWelcomeTokenQuestsHandler, self).__init__((SYS_MESSAGE_TYPE.tokenQuests.index(), SYS_MESSAGE_TYPE.battleResults.index()), awardCtrl)

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
