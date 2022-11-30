# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_constants.py
from collections import namedtuple
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import Resource
from gui.impl.gen.view_models.views.lobby.new_year.ny_tabs import ChallengeViewTabs, FriendGladeViewTabs
from items.components.ny_constants import CurrentNYConstants, CustomizationObjects, PREV_NY_TOYS_COLLECTIONS, YEARS, YEARS_INFO
from ny_common.settings import GuestsQuestsConsts
from shared_utils import CONST_CONTAINER

class AnchorNames(CONST_CONTAINER):
    TREE = 'ChristmasTree'
    FIELD_KITCHEN = 'FieldKitchen'
    SCULPTURE = 'SnowSculpture'
    ILLUMINATION = 'OuterTreesIllumination'
    CELEBRITY = 'CelebrityPlace'
    CELEBRITY_A = 'Celebrity_1'
    CELEBRITY_M = 'Celebrity_2'
    CELEBRITY_CAT = 'Celebrity_3'
    CELEBRITY_D = 'Dog'
    CHALLENGE = 'Challenge'
    MARKETPLACE = 'Marketplace'
    RESOURCES = 'CraftPlace_SpaceDust'
    GIFT_MACHINE = 'GiftMachine'
    GIFT_MACHINE_SIDE = 'GiftMachineSide'
    GIFT_MACHINE_CLOSE = 'GiftMachineClose'
    UNDER_SPACE = 'Megazone'
    CELEBRITY_COMPLETED = 'CelebrityCompleted'


class AdditionalCameraObject(CONST_CONTAINER):
    CELEBRITY = 'Celebrity'
    CELEBRITY_A = 'CelebrityA'
    CELEBRITY_M = 'CelebrityM'
    CELEBRITY_CAT = 'CelebrityC'
    CELEBRITY_D = 'CelebrityD'
    CHALLENGE = 'Challenge'
    MARKETPLACE = 'Marketplace'
    RESOURCES = 'Resources'
    GIFT_MACHINE = 'GiftMachine'
    GIFT_MACHINE_CLOSE = 'GiftMachineClose'
    GIFT_MACHINE_SIDE = 'GiftMachineSide'
    GIFT_MACHINE_VEH_PREVIEW = 'GiftMachineVehiclePreview'
    UNDER_SPACE = 'UnderSpace'
    CELEBRITY_GROUP = (CHALLENGE,
     CELEBRITY_A,
     CELEBRITY_M,
     CELEBRITY_CAT,
     CELEBRITY,
     CELEBRITY_D)
    GIFT_MACHINE_GROUP = (GIFT_MACHINE, GIFT_MACHINE_CLOSE, GIFT_MACHINE_SIDE)


ANCHOR_TO_OBJECT = {AnchorNames.TREE: CustomizationObjects.FIR,
 AnchorNames.FIELD_KITCHEN: CustomizationObjects.FAIR,
 AnchorNames.SCULPTURE: CustomizationObjects.INSTALLATION,
 AnchorNames.MARKETPLACE: AdditionalCameraObject.MARKETPLACE,
 AnchorNames.CELEBRITY: AdditionalCameraObject.CELEBRITY,
 AnchorNames.CELEBRITY_A: AdditionalCameraObject.CELEBRITY_A,
 AnchorNames.CELEBRITY_M: AdditionalCameraObject.CELEBRITY_M,
 AnchorNames.CELEBRITY_CAT: AdditionalCameraObject.CELEBRITY_CAT,
 AnchorNames.CELEBRITY_D: AdditionalCameraObject.CELEBRITY_D,
 AnchorNames.CHALLENGE: AdditionalCameraObject.CHALLENGE,
 AnchorNames.RESOURCES: AdditionalCameraObject.RESOURCES,
 AnchorNames.GIFT_MACHINE: AdditionalCameraObject.GIFT_MACHINE,
 AnchorNames.GIFT_MACHINE_SIDE: AdditionalCameraObject.GIFT_MACHINE_SIDE,
 AnchorNames.GIFT_MACHINE_CLOSE: AdditionalCameraObject.GIFT_MACHINE_CLOSE,
 AnchorNames.UNDER_SPACE: AdditionalCameraObject.UNDER_SPACE}
OBJECT_TO_ANCHOR = {v:k for k, v in ANCHOR_TO_OBJECT.iteritems()}
UPGRADABLE_OBJECTS = (CustomizationObjects.FIR, CustomizationObjects.FAIR, CustomizationObjects.INSTALLATION)
GLADE_OBJECTS = (AdditionalCameraObject.UNDER_SPACE,
 AdditionalCameraObject.RESOURCES,
 CustomizationObjects.FIR,
 CustomizationObjects.FAIR,
 CustomizationObjects.INSTALLATION)
MAX_LEVEL = 10
TOY_PREFIX = 'toy_'
NY_LEVEL_PREFIX = 'ny23:level'
TOY_COLLECTIONS = PREV_NY_TOYS_COLLECTIONS + [CurrentNYConstants.TOYS]
NY_COLLECTION_PREFIXES = ('ny19:cr', 'ny20:cr', 'ny21:cr', 'ny22:cr', 'ny23:cr')
NY_COLLECTION_MEGA_PREFIX = 'ny23:cr:mega'
NY_OLD_COLLECTION_PREFIX = 'ny18:cr'
TANK_SLOT_BONUS_ORDER = ['xpFactor', 'tankmenXPFactor', 'freeXPFactor']
NY_TUTORIAL_NOTIFICATION_LOCK_KEY = 'nyTutorial'
NY_LEVEL_UP_NOTIFICATION_LOCK_KEY = 'nyLevelUpAnimation'
_ACTION_TOKEN_DECORATION_ID_TO_UI = {'ny23:guest_A:decoration:1': 'headquarters',
 'ny23:guest_A:decoration:2': 'snowman',
 'ny23:guest_A:decoration:3': 'train',
 'ny23:guest_M:decoration:1': 'bridge',
 'ny23:guest_M:decoration:2': 'rink',
 'ny23:guest_M:decoration:3': 'vehicle'}
GUEST_ECONOMIC_BONUS_ID = 'ny23GuestEconomic'
NY_MARKETPLACE_UNLOCK = 'ny23:marketplace_unlock'

class GuestsQuestsTokens(GuestsQuestsConsts):
    GUEST_TOKEN = 'guest_'
    ACTION_TOKEN_PREFIX = '{}:{}'.format(YEARS_INFO.CURRENT_YEAR_STR, GUEST_TOKEN)
    TOKEN_CAT = 'guest_cat_unlock'
    TOKEN_DOG = 'ny23:dog_unlock'
    GUEST_A = '{}{}'.format(GUEST_TOKEN, 'A')
    GUEST_M = '{}{}'.format(GUEST_TOKEN, 'M')
    GUEST_C = '{}{}'.format(GUEST_TOKEN, 'cat')
    GUESTS_ALL = (GUEST_A, GUEST_M, GUEST_C)
    GUEST_A_COMPLETED = '{}_quest_complete'.format(GUEST_A)
    GUEST_M_COMPLETED = '{}_quest_complete'.format(GUEST_M)
    GUEST_C_COMPLETED = '{}_quest_complete'.format(GUEST_C)
    GUEST_ALL_COMPLETED = (GUEST_A_COMPLETED, GUEST_M_COMPLETED, GUEST_C_COMPLETED)
    GUEST_DEPENDENCIES = GUEST_ALL_COMPLETED + (TOKEN_CAT,)
    ECONOMIC_GUESTS_TOKENS = (GUEST_A_COMPLETED, GUEST_M_COMPLETED)

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
        return '{}:{}:{}:{}'.format(YEARS_INFO.CURRENT_YEAR_STR, guestName, actionType, level)


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


class MegaDecorationTokens(object):
    AIRSHIP = 'ny23:deco:airship'
    FERRIS_WHEEL = 'ny23:deco:ferriswheel'
    CHALET = 'ny23:deco:chalet'
    ALL = (AIRSHIP, FERRIS_WHEEL, CHALET)


class Collections(CONST_CONTAINER):
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
    AUTO_COLLECTING_STATS = 'autoCollectingStats'
    STROKE_COUNT = 'strokeCount'
    PIGGY_BANK_ACTIVE_ITEM_INDEX = 'nyPiggyBankActiveItemIndex'


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
    TOWN = AdditionalCameraObject.UNDER_SPACE
    FIR = CustomizationObjects.FIR
    FAIR = CustomizationObjects.FAIR
    INSTALLATION = CustomizationObjects.INSTALLATION
    RESOURCES = AdditionalCameraObject.RESOURCES
    ALL = (TOWN,
     FIR,
     FAIR,
     INSTALLATION,
     RESOURCES)


class NyTabBarMarketplaceView(object):
    NY18_CATEGORY = Collections.NewYear18
    NY19_CATEGORY = Collections.NewYear19
    NY20_CATEGORY = Collections.NewYear20
    NY21_CATEGORY = Collections.NewYear21
    NY22_CATEGORY = Collections.NewYear22
    ALL = (NY18_CATEGORY,
     NY19_CATEGORY,
     NY20_CATEGORY,
     NY21_CATEGORY,
     NY22_CATEGORY)
    REVERSED_ALL = tuple(reversed(ALL))


class NyTabBarChallengeView(object):
    TOURNAMENT = ChallengeViewTabs.TOURNAMENT.value
    TOURNAMENT_COMPLETED = ChallengeViewTabs.TOURNAMENTCOMPLETED.value
    GUEST_A = ChallengeViewTabs.GUESTA.value
    GUEST_M = ChallengeViewTabs.GUESTM.value
    GUEST_CAT = ChallengeViewTabs.GUESTC.value
    HEADQUARTERS = ChallengeViewTabs.HEADQUARTERS.value
    GUEST_D = ChallengeViewTabs.GUESTD.value
    ALL = (TOURNAMENT,
     GUEST_A,
     GUEST_M,
     GUEST_CAT,
     HEADQUARTERS,
     GUEST_D)


class NyTabBarFriendGladeView(object):
    TOWN = FriendGladeViewTabs.TOWN.value
    FIR = FriendGladeViewTabs.FIR.value
    FAIR = FriendGladeViewTabs.FAIR.value
    INSTALLATION = FriendGladeViewTabs.INSTALLATION.value
    RESOURCES = FriendGladeViewTabs.RESOURCES.value
    ALL = (TOWN,
     FIR,
     FAIR,
     INSTALLATION,
     RESOURCES)


CHALLENGE_TAB_TO_CAMERA_OBJ = {NyTabBarChallengeView.TOURNAMENT: AdditionalCameraObject.CHALLENGE,
 NyTabBarChallengeView.TOURNAMENT_COMPLETED: AdditionalCameraObject.CHALLENGE,
 NyTabBarChallengeView.GUEST_A: AdditionalCameraObject.CELEBRITY_A,
 NyTabBarChallengeView.GUEST_M: AdditionalCameraObject.CELEBRITY_M,
 NyTabBarChallengeView.GUEST_CAT: AdditionalCameraObject.CELEBRITY_CAT,
 NyTabBarChallengeView.GUEST_D: AdditionalCameraObject.CELEBRITY_D,
 NyTabBarChallengeView.HEADQUARTERS: AdditionalCameraObject.CELEBRITY}
FRIEND_GLADE_TAB_TO_OBJECTS = {NyTabBarFriendGladeView.TOWN: AdditionalCameraObject.UNDER_SPACE,
 NyTabBarFriendGladeView.FIR: CustomizationObjects.FIR,
 NyTabBarFriendGladeView.FAIR: CustomizationObjects.FAIR,
 NyTabBarFriendGladeView.INSTALLATION: CustomizationObjects.INSTALLATION,
 NyTabBarFriendGladeView.RESOURCES: AdditionalCameraObject.RESOURCES}
CAMERA_OBJ_TO_FRIEND_GLADE_TAB = {o:t for t, o in FRIEND_GLADE_TAB_TO_OBJECTS.items()}
CHALLENGE_CAMERA_OBJ_TO_TAB = {AdditionalCameraObject.CHALLENGE: NyTabBarChallengeView.TOURNAMENT,
 AdditionalCameraObject.CELEBRITY_A: NyTabBarChallengeView.GUEST_A,
 AdditionalCameraObject.CELEBRITY_M: NyTabBarChallengeView.GUEST_M,
 AdditionalCameraObject.CELEBRITY_CAT: NyTabBarChallengeView.GUEST_CAT,
 AdditionalCameraObject.CELEBRITY_D: NyTabBarChallengeView.GUEST_D,
 AdditionalCameraObject.CELEBRITY: NyTabBarChallengeView.HEADQUARTERS}
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
