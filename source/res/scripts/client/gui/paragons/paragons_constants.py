# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/paragons/paragons_constants.py
from shared_utils import CONST_CONTAINER
from gui.impl.gen import R

class ParagonsSystemMessages(CONST_CONTAINER):
    PROJECT_IS_AVAILABLE = 'projectIsAvailable'
    BRANCH_RESET_IS_AVAILABLE = 'branchResetIsAvailable'
    PROJECT_IS_CONTINUING = 'projectIsContinuing'
    NEW_CHAPTER_IS_AVAILABLE = 'newStageIsAvailable'
    PROJECT_IS_UNAVAILABLE = 'projectIsUnavailable'
    BRANCH_RESET_ERROR = 'paragonsBranchResetError'
    BATTLE_REWARD = 'paragonsBattleReward'
    LEVEL_REWARDS = 'paragonsLevelReward'
    LEVEL_SELECTABLE_REWARDS = 'paragonsLevelSelectableReward'
    BRANCH_RESETED = 'paragonsBranchReseted'
    BRANCH_IS_UNAVAILABLE = 'paragonsBranchIsUnavailable'
    BRANCH_IS_AVAILABLE = 'paragonsBranchIsAvailable'
    FIRST_MAIN_REWARD_ACHIEVED = 'paragonsFirstMainRewardBadgeAchieved'
    CHAPTER_COMPLETED = 'paragonsChapterCompleted'
    CHAPTER_1_COMPLETED = 'paragons_S1_completed'
    CHAPTER_2_COMPLETED = 'paragons_S2_completed'
    CHAPTER_COMPLETE_MESSAGES = {1: CHAPTER_1_COMPLETED,
     2: CHAPTER_2_COMPLETED}

    @classmethod
    def getChapterCompleteMessage(cls, chapterID):
        return cls.CHAPTER_COMPLETE_MESSAGES.get(chapterID)


MESSAGE_ICONS = {ParagonsSystemMessages.FIRST_MAIN_REWARD_ACHIEVED: R.images.gui.maps.icons.paragons.messenger.notification_icon_first11,
 ParagonsSystemMessages.CHAPTER_1_COMPLETED: R.images.gui.maps.icons.paragons.messenger.notification_icon_first_chapter,
 ParagonsSystemMessages.CHAPTER_2_COMPLETED: R.images.gui.maps.icons.paragons.messenger.notification_icon_chapter_S2}
PARAGONS_POST_BATTLE_FAKE_QUEST_ID = 'paragonsFakeQuestID'
