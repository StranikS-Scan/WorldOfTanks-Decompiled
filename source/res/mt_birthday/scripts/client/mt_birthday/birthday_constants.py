# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/birthday_constants.py
from constants import ARENA_BONUS_TYPE
from constants_utils import ConstInjector
from messenger import m_constants
from shared_utils import CONST_CONTAINER
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.birthday_main_view_model import TabId
BIRTHDAY_STAMP_CODE = 'giftsystem_5_stamp'
BIRTHDAY_GOLDEN_TICKET = 'birthday2026_golden_ticket'
BIRTHDAY_STAMP_CODE_SPECIAL = 'giftsystem_5_stampSpecial'
BIRTHDAY_BLOGGER_TOKEN = 'birthday_26_blogger_token'
BIRTHDAY_GOLDEN_TICKET_CURRENCY = 'goldenticket'
BIRTHDAY_REPLY_GIFT_TOKEN = 'birthday_26_rg_token'
LAST_BATTLES_PLAYERS_SAVE_COUNT = 5
POST_BATTLE_EXTRA_TAB_UI = 'PostbattleExtraTabUI'
POST_BATTLE_REDEFINED_TAB_UI = 'GiftSystemTeamStatsUI'
BIRTHDAY_BLOGGER_LOOTBOX_TAG = 'bloggerLootBox'

class BirthdayLootBoxes(CONST_CONTAINER):
    LARGE = 'tanks_birthday_2026_large'
    SMALL = 'tanks_birthday_2026_small'


class AnchorNames(CONST_CONTAINER):
    GOLD_WAGON = 'GoldWagon'
    POST_OFFICE = 'PostOffice'
    QUEST_GIVER = 'QuestGiver'


CUSTOM_NOTIFICATION_NAME = 'BirthdayBonusNotification'
CUSTOM_GIFT_NOTIFICATION_NAME = 'BirthdayGiftNotification'

class GFNotificationTemplates(m_constants.GFNotificationTemplates, ConstInjector):
    CUSTOM_BIRTHDAY_GIFT_NOTIFICATION = CUSTOM_GIFT_NOTIFICATION_NAME
    CUSTOM_BIRTHDAY_BONUS_NOTIFICATION = CUSTOM_NOTIFICATION_NAME


class BirthdayStorageKeys(CONST_CONTAINER):
    MT_BIRTHDAY = 'MT_BIRTHDAY'
    BIRTHDAY_WELCOME_NOTIFICATION = 'BirthdayWelcomeNotification'
    GIFT_RECEIVED = 'GIFT_RECEIVED'
    BONUS_RECEIVED = 'BONUS_RECEIVED'
    BIRTHDAY_GENERAL_TIPS_SEEN = 'BirthdayGeneralTipsSeen'
    BIRTHDAY_MAIL_TIPS_SEEN = 'BirthdayMailTipsSeen'
    BIRTHDAY_QUEST_GIVER_TIPS_SEEN = 'BirthdayQuestGiverTipsSeen'
    BIRTHDAY_GOLD_WAGON_TIPS_SEEN = 'BirthdayGoldWagonTipsSeen'
    BIRTHDAY_TICKET_EXCHANGE_TIPS_SEEN = 'BirthdayTicketExchangeTipsSeen'


ACCOUNT_DEFAULT_SETTINGS = {BirthdayStorageKeys.MT_BIRTHDAY: {BirthdayStorageKeys.BIRTHDAY_WELCOME_NOTIFICATION: False,
                                   BirthdayStorageKeys.GIFT_RECEIVED: False,
                                   BirthdayStorageKeys.BONUS_RECEIVED: False,
                                   BirthdayStorageKeys.BIRTHDAY_GENERAL_TIPS_SEEN: False,
                                   BirthdayStorageKeys.BIRTHDAY_MAIL_TIPS_SEEN: False,
                                   BirthdayStorageKeys.BIRTHDAY_QUEST_GIVER_TIPS_SEEN: False,
                                   BirthdayStorageKeys.BIRTHDAY_GOLD_WAGON_TIPS_SEEN: False,
                                   BirthdayStorageKeys.BIRTHDAY_TICKET_EXCHANGE_TIPS_SEEN: False}}
TAB_ID_TO_ACCOUNT_SETTING = {TabId.MAIL: BirthdayStorageKeys.BIRTHDAY_MAIL_TIPS_SEEN,
 TabId.QUESTS: BirthdayStorageKeys.BIRTHDAY_QUEST_GIVER_TIPS_SEEN,
 TabId.GOLD_WAGON: BirthdayStorageKeys.BIRTHDAY_GOLD_WAGON_TIPS_SEEN,
 TabId.TICKET_EXCHANGE: BirthdayStorageKeys.BIRTHDAY_TICKET_EXCHANGE_TIPS_SEEN}
MT_BIRTHDAY_EVENT_STATE = {'Active': 'Active',
 'Paused': 'Paused',
 'Disabled': 'Disabled'}
SUPPORTED_POST_BATTLE_BONUS_TYPES = ARENA_BONUS_TYPE.RANDOM_RANGE + (ARENA_BONUS_TYPE.SORTIE_2, ARENA_BONUS_TYPE.FORT_BATTLE_2)

def isBirthdayQuestGiverQuest(questID):
    return questID.startswith('mt_birthday_quest_giver')
