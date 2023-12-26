# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_constants.py
from collections import namedtuple
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import Resource
from gui.impl.gen.view_models.views.lobby.new_year.ny_tabs import ChallengeViewTabs, FriendGladeViewTabs
from items.components.ny_constants import CurrentNYConstants, CustomizationObjects, PREV_NY_TOYS_COLLECTIONS, YEARS, YEARS_INFO
from ny_common.settings import GuestsQuestsConsts
from shared_utils import CONST_CONTAINER

class NYObjects(CONST_CONTAINER):
    TREE = CustomizationObjects.FIR
    FIELD_KITCHEN = CustomizationObjects.FAIR
    SCULPTURE = CustomizationObjects.INSTALLATION
    ILLUMINATION = 'OuterTreesIllumination'
    CELEBRITY = 'CelebrityPlace'
    CELEBRITY_A = 'Celebrity_1'
    CELEBRITY_CAT = 'Celebrity_3'
    CELEBRITY_D = 'Dog'
    CHALLENGE = 'Challenge'
    MARKETPLACE = 'Marketplace'
    RESOURCES = 'Resources'
    GIFT_MACHINE = 'GiftMachine'
    GIFT_MACHINE_SIDE = 'GiftMachineSide'
    TOWN = 'Town'
    CELEBRITY_GROUP = (CHALLENGE,
     CELEBRITY_A,
     CELEBRITY_CAT,
     CELEBRITY,
     CELEBRITY_D)
    UPGRADABLE_GROUP = (TREE, FIELD_KITCHEN, SCULPTURE)


class MegaDecorationsObjects(CONST_CONTAINER):
    BRIDGE = 'Bridge_Camera'
    WHEEL = 'Wheel_Camera'
    CASTLE = 'Castle_Camera'


GLADE_OBJECTS = (NYObjects.TOWN,
 NYObjects.RESOURCES,
 NYObjects.TREE,
 NYObjects.FIELD_KITCHEN,
 NYObjects.SCULPTURE)
TOY_PREFIX = 'toy_'
NY_LEVEL_PREFIX = 'ny:level'
TOY_COLLECTIONS = PREV_NY_TOYS_COLLECTIONS + [CurrentNYConstants.TOYS]
NY_COLLECTION_PREFIXES = ('ny19:cr', 'ny20:cr', 'ny21:cr', 'ny22:cr', 'ny23:cr', 'ny24:cr')
NY_COLLECTION_MEGA_PREFIX = '{}:cr:mega'.format(YEARS_INFO.CURRENT_YEAR_STR)
NY_OLD_COLLECTION_PREFIX = 'ny18:cr'
TANK_SLOT_BONUS_ORDER = ['xpFactor', 'tankmenXPFactor', 'freeXPFactor']
NY_TUTORIAL_NOTIFICATION_LOCK_KEY = 'nyTutorial'
NY_LEVEL_UP_NOTIFICATION_LOCK_KEY = 'nyLevelUpAnimation'
_ACTION_TOKEN_DECORATION_ID_TO_UI = {'ny:guest_A:decoration:1': 'headquarters',
 'ny:guest_A:decoration:2': 'snowman',
 'ny:guest_A:decoration:3': 'train'}
GUEST_ECONOMIC_BONUS_ID = 'nyGuestEconomic'
NY_MARKETPLACE_UNLOCK = 'ny:marketplace_unlock'
NY_ATM_AWARD_SCREEN_LEVELS = [2, 10]
DAYS_BETWEEN_FRIEND_TAB_REMINDER = 3

class GuestsQuestsTokens(GuestsQuestsConsts):
    GUEST_TOKEN = 'guest_'
    ACTION_TOKEN_PREFIX = 'ny:{}'.format(GUEST_TOKEN)
    TOKEN_CAT = 'ny:cat_unlock'
    TOKEN_DOG = 'ny:dog_unlock'
    GUEST_A = '{}{}'.format(GUEST_TOKEN, 'A')
    GUEST_C = '{}{}'.format(GUEST_TOKEN, 'cat')
    GUESTS_ALL = (GUEST_A, GUEST_C)
    GUEST_A_COMPLETED = '{}_quest_complete'.format(GUEST_A)
    GUEST_C_COMPLETED = '{}_quest_complete'.format(GUEST_C)
    GUEST_ALL_COMPLETED = (GUEST_A_COMPLETED, GUEST_C_COMPLETED)
    GUEST_DEPENDENCIES = GUEST_ALL_COMPLETED + (TOKEN_CAT,)
    ECONOMIC_GUESTS_TOKENS = (GUEST_A_COMPLETED,)

    @classmethod
    def getGuestCompletedTokenName(cls, guestName):
        return '{}_quest_complete'.format(guestName) if guestName in cls.GUESTS_ALL else None

    @classmethod
    def getUIActionIconID(cls, tokenID):
        _, actionType, _ = parseCelebrityTokenActionType(tokenID)
        return _ACTION_TOKEN_DECORATION_ID_TO_UI.get(tokenID) if actionType == GuestQuestTokenActionType.DECORATION else actionType

    @classmethod
    def isActionToken(cls, tokenID):
        _, actionType, __ = parseCelebrityTokenActionType(tokenID)
        return actionType in GuestQuestTokenActionType.ALL

    @classmethod
    def generateDefaultActionToken(cls, guestName, actionType, level=''):
        return 'ny:{}:{}:{}'.format(guestName, actionType, level)


class GuestQuestTokenActionType(object):
    ANIM = 'anim'
    STORY = 'story'
    DECORATION = 'decoration'
    ALL = (ANIM, STORY, DECORATION)


def parseCelebrityTokenActionType(tokenID):
    guestName = None
    actionType = None
    level = None
    if tokenID.startswith(GuestsQuestsTokens.ACTION_TOKEN_PREFIX) and len(tokenID.split(':')) > 3:
        splited = tokenID.split(':')
        guestName = splited[1]
        actionType = splited[2]
        try:
            level = splited[-1]
            level = int(level) if level != '' and int(level) >= 0 else None
        except ValueError:
            return (guestName, actionType, level)

    return (guestName, actionType, level)


class Collections(CONST_CONTAINER):
    NewYear24 = YEARS.getYearStrFromYearNum(24)
    NewYear23 = YEARS.getYearStrFromYearNum(23)
    NewYear22 = YEARS.getYearStrFromYearNum(22)
    NewYear21 = YEARS.getYearStrFromYearNum(21)
    NewYear20 = YEARS.getYearStrFromYearNum(20)
    NewYear19 = YEARS.getYearStrFromYearNum(19)
    NewYear18 = YEARS.getYearStrFromYearNum(18)

    @classmethod
    def SORTED_ALL(cls, comparator=None, key=None, reverse=False):
        return sorted(tuple(cls.ALL()), cmp=comparator, key=key, reverse=reverse)


class SyncDataKeys(CONST_CONTAINER):
    INVENTORY_TOYS = 'inventoryToys'
    SLOTS = 'slots'
    FRIEND_SLOTS = 'friendSlots'
    LEVEL = 'level'
    POINTS = 'atmospherePoints'
    TOY_COLLECTION = 'toyCollection'
    COLLECTION_DISTRIBUTIONS = 'collectionDistributions'
    VEHICLE_BONUS_CHOICES = 'bonusChoices'
    SELECTED_DISCOUNTS = 'selectedDiscounts'
    OBJECTS_LEVELS = 'objectsLevels'
    XP_BONUS_CHOICE = 'xpBonusChoice'
    COMPLETED_GUEST_QUESTS = 'lastCompletedGuestQuestsIndexes'
    HANGAR_NAME_MASK = 'hangarNameMask'
    RESOURCE_COLLECTING = 'resourceCollecting'
    STROKE_COUNT = 'strokeCount'
    PIGGY_BANK_ACTIVE_ITEM_INDEX = 'nyPiggyBankActiveItemIndex'
    PREV_NY_LEVEL = 'prevNYLevel'


class FormulaInfo(object):
    MULTIPLIER = 0
    COLLECTION_BONUS = 1


class NyWidgetTopMenu(object):
    INFO = 'info'
    GLADE = 'glade'
    REWARDS = 'rewards'
    MARKETPLACE = 'marketplace'
    GIFT_MACHINE = 'gift'
    COLLECTIONS = 'collections'
    FRIENDS = 'friends'
    CHALLENGE = 'challenge'
    FRIEND_GLADE = 'friendGlade'
    FRIEND_CHALLENGE = 'friendChallenge'
    FRIEND_INFO = 'friendInfo'
    ALL_PLAYER_HANGAR = (GLADE,
     FRIENDS,
     CHALLENGE,
     MARKETPLACE,
     GIFT_MACHINE,
     REWARDS,
     INFO)
    ALL_FRIEND_HANGAR = (FRIEND_GLADE, FRIEND_CHALLENGE, FRIEND_INFO)


class NyTabBarMainView(object):
    TOWN = NYObjects.TOWN
    FIR = NYObjects.TREE
    FAIR = NYObjects.FIELD_KITCHEN
    INSTALLATION = NYObjects.SCULPTURE
    RESOURCES = NYObjects.RESOURCES
    ALL = (RESOURCES,
     TOWN,
     FIR,
     FAIR,
     INSTALLATION)


class NyTabBarMarketplaceView(object):
    NY18_CATEGORY = Collections.NewYear18
    NY19_CATEGORY = Collections.NewYear19
    NY20_CATEGORY = Collections.NewYear20
    NY21_CATEGORY = Collections.NewYear21
    NY22_CATEGORY = Collections.NewYear22
    NY23_CATEGORY = Collections.NewYear23
    ALL = (NY18_CATEGORY,
     NY19_CATEGORY,
     NY20_CATEGORY,
     NY21_CATEGORY,
     NY22_CATEGORY,
     NY23_CATEGORY)
    REVERSED_ALL = tuple(reversed(ALL))


class NyTabBarChallengeView(object):
    TOURNAMENT = ChallengeViewTabs.TOURNAMENT.value
    TOURNAMENT_COMPLETED = ChallengeViewTabs.TOURNAMENTCOMPLETED.value
    GUEST_A = ChallengeViewTabs.GUESTA.value
    GUEST_CAT = ChallengeViewTabs.GUESTC.value
    HEADQUARTERS = ChallengeViewTabs.HEADQUARTERS.value
    GUEST_D = ChallengeViewTabs.GUESTD.value
    ALL = (TOURNAMENT,
     GUEST_A,
     GUEST_CAT,
     HEADQUARTERS,
     GUEST_D)


class NyTabBarFriendGladeView(object):
    TOWN = FriendGladeViewTabs.TOWN.value
    FIR = FriendGladeViewTabs.FIR.value
    FAIR = FriendGladeViewTabs.FAIR.value
    INSTALLATION = FriendGladeViewTabs.INSTALLATION.value
    RESOURCES = FriendGladeViewTabs.RESOURCES.value
    ALL = (RESOURCES,
     TOWN,
     FIR,
     FAIR,
     INSTALLATION)


CHALLENGE_TAB_TO_CAMERA_OBJ = {NyTabBarChallengeView.TOURNAMENT: NYObjects.CHALLENGE,
 NyTabBarChallengeView.TOURNAMENT_COMPLETED: NYObjects.CHALLENGE,
 NyTabBarChallengeView.GUEST_A: NYObjects.CELEBRITY_A,
 NyTabBarChallengeView.GUEST_CAT: NYObjects.CELEBRITY_CAT,
 NyTabBarChallengeView.GUEST_D: NYObjects.CELEBRITY_D,
 NyTabBarChallengeView.HEADQUARTERS: NYObjects.CELEBRITY}
GLADE_TAB_TO_OBJECTS = {NyTabBarMainView.TOWN: NYObjects.TOWN,
 NyTabBarMainView.FIR: NYObjects.TREE,
 NyTabBarMainView.FAIR: NYObjects.FIELD_KITCHEN,
 NyTabBarMainView.INSTALLATION: NYObjects.SCULPTURE,
 NyTabBarMainView.RESOURCES: NYObjects.RESOURCES}
FRIEND_GLADE_TAB_TO_OBJECTS = {NyTabBarFriendGladeView.TOWN: NYObjects.TOWN,
 NyTabBarFriendGladeView.FIR: NYObjects.TREE,
 NyTabBarFriendGladeView.FAIR: NYObjects.FIELD_KITCHEN,
 NyTabBarFriendGladeView.INSTALLATION: NYObjects.SCULPTURE,
 NyTabBarFriendGladeView.RESOURCES: NYObjects.RESOURCES}
CAMERA_OBJ_TO_FRIEND_GLADE_TAB = {o:t for t, o in FRIEND_GLADE_TAB_TO_OBJECTS.items()}
CHALLENGE_CAMERA_OBJ_TO_TAB = {NYObjects.CHALLENGE: NyTabBarChallengeView.TOURNAMENT,
 NYObjects.CELEBRITY_A: NyTabBarChallengeView.GUEST_A,
 NYObjects.CELEBRITY_CAT: NyTabBarChallengeView.GUEST_CAT,
 NYObjects.CELEBRITY_D: NyTabBarChallengeView.GUEST_D,
 NYObjects.CELEBRITY: NyTabBarChallengeView.HEADQUARTERS}
NewYearSysMessages = namedtuple('NewYearSysMessages', 'keyText, priority, type')
RESOURCES_ORDER = (Resource.CRYSTAL,
 Resource.EMERALD,
 Resource.AMBER,
 Resource.IRON)

class NyBonusNames(CONST_CONTAINER):
    VEHICLE_SLOT = 'newYearSlot'


class NyResourceCollectingStats(CONST_CONTAINER):
    RESOURCES = 'resources'
    SPENT_MONEY = 'price'
    COUNT = 'count'


class MarkerObjects(CONST_CONTAINER):
    FIR = NYObjects.TREE
    FAIR = NYObjects.FIELD_KITCHEN
    INSTALLATION = NYObjects.SCULPTURE


class NyGFNotificationTemplates(CONST_CONTAINER):
    NY_SACKS_RARE_LOOT = 'NySackRareLoot'
    NY_NEW_REWARD_KIT = 'NyNewRewardKit'
    NY_DOG_REMINDER = 'NyDogReminderMessage'
    NY_DOG_MISSION_COMPLETED = 'NyDogMissionCompleted'
    NY_RECEIVING_AWARDS = 'NyReceivingAwards'
    NY_CHALLENGE_REWARDS = 'NyChallengeRewards'
    NY_CHALLENGE_QUEST = 'NyChallengeQuest'
    NY_QUEST_REWARDS = 'NyQuestRewards'
    NY_RESOURCES_REMINDER = 'NyResourcesReminder'
    NY_PIGGY_BANK_ONE_REWARD = 'NyPiggyBankSingleReward'
    NY_PIGGY_BANK_MULTIPLE_REWARDS = 'NyPiggyBankMultipleRewards'


class AdventCalendarGFNotificationTemplates(CONST_CONTAINER):
    ADVENT_CALENDAR_DOORS_AVAILABLE_FIRST_ENTRY = 'AdventCalendarV2DoorsAvailableFirstEntry'
    ADVENT_CALENDAR_DOORS_AVAILABLE = 'AdventCalendarV2DoorsAvailable'
    ADVENT_CALENDAR_DOORS_AVAILABLE_POST_EVENT = 'AdventCalendarV2DoorsAvailablePostEvent'
