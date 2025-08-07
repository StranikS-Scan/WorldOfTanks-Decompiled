# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/birthday_constants.py
from constants_utils import ConstInjector
from messenger import m_constants
from shared_utils import CONST_CONTAINER
BIRTHDAY_2025_STAMP_CODE = 'giftsystem_4_stamp'
BIRTHDAY_2025_GOLDEN_TICKET = 'birthday2025_golden_ticket'
BIRTHDAY_2025_STAMP_CODE_SPECIAL = 'giftsystem_4_stampSpecial'
BIRTHDAY_2025_BLOGGER_TOKEN = 'birthday_25_blogger_token'
LAST_BATTLES_PLAYERS_SAVE_COUNT = 5
POST_BATTLE_EXTRA_TAB_UI = 'PostbattleExtraTabUI'
BIRTHDAY_2025_BLOGGER_LOOTBOX_TAG = 'bloggerLootBox'

class BirthdayLootBoxes(CONST_CONTAINER):
    LARGE = 'tanks_birthday_2025_large'
    SMALL = 'tanks_birthday_2025_small'


class AnchorNames(CONST_CONTAINER):
    GOLD_WAGON = 'GoldWagon'
    POST_OFFICE = 'PostOffice'


CUSTOM_NOTIFICATION_NAME = 'BirthdayBonusNotification'
CUSTOM_GIFT_NOTIFICATION_NAME = 'BirthdayGiftNotification'

class GFNotificationTemplates(m_constants.GFNotificationTemplates, ConstInjector):
    CUSTOM_BIRTHDAY_GIFT_NOTIFICATION = CUSTOM_GIFT_NOTIFICATION_NAME
    CUSTOM_BIRTHDAY_BONUS_NOTIFICATION = CUSTOM_NOTIFICATION_NAME


class BirthdayStorageKeys(CONST_CONTAINER):
    MT_BIRTHDAY = 'MT_BIRTHDAY'
    INTRO_SEEN = 'INTRO_SEEN'
    BIRTHDAY_WELCOME_NOTIFICATION = 'BirthdayWelcomeNotification'
    GIFT_RECEIVED = 'GIFT_RECEIVED'
    BONUS_RECEIVED = 'BONUS_RECEIVED'


ACCOUNT_DEFAULT_SETTINGS = {BirthdayStorageKeys.MT_BIRTHDAY: {BirthdayStorageKeys.INTRO_SEEN: False,
                                   BirthdayStorageKeys.BIRTHDAY_WELCOME_NOTIFICATION: False,
                                   BirthdayStorageKeys.GIFT_RECEIVED: False,
                                   BirthdayStorageKeys.BONUS_RECEIVED: False}}
MT_BIRTHDAY_EVENT_STATE = {'Active': 'Active',
 'Paused': 'Paused',
 'Disabled': 'Disabled'}
