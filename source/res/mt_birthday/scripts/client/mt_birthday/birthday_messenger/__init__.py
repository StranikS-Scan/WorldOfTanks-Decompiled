# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/birthday_messenger/__init__.py
from gui.impl.gen import R
from gui.shared.system_factory import registerTokenQuestsSubFormatters, registerNotificationsListeners, registerServiceChannelSubformatter

def registerCustomMessages():
    from gui.impl.lobby.gf_notifications import PresentersFactory
    from mt_birthday.gui.impl.lobby.birthday.notifications.lootbox_notification import LootboxNotification, GiftLootboxNotification
    from mt_birthday.birthday_constants import CUSTOM_NOTIFICATION_NAME, CUSTOM_GIFT_NOTIFICATION_NAME
    from mt_birthday.birthday_messenger.listeners import BirthdayBonusLootboxListener, BirthdayGiftLootboxListener
    PresentersFactory.add(CUSTOM_NOTIFICATION_NAME, R.views.mt_birthday.lobby.notifications.LootboxNotificationView(), LootboxNotification)
    PresentersFactory.add(CUSTOM_GIFT_NOTIFICATION_NAME, R.views.mt_birthday.lobby.notifications.LootboxNotificationView(), GiftLootboxNotification)
    registerNotificationsListeners((BirthdayBonusLootboxListener, BirthdayGiftLootboxListener))


def registerBirthdayTokenQuestsSubFormatters():
    from mt_birthday.birthday_messenger.formatters.token_quest_subformatters import BirthdayLevelUpFormatter
    registerTokenQuestsSubFormatters((BirthdayLevelUpFormatter(),))


def registerBirthdayLootboxCashBackListener():
    from mt_birthday.birthday_messenger.listeners import BirthdayLootboxCashBackListener
    registerNotificationsListeners((BirthdayLootboxCashBackListener,))
