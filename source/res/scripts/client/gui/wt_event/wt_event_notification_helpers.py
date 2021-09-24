# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wt_event/wt_event_notification_helpers.py
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.bonuses import getMergedBonusesFromDicts
from gui.shared.formatters import formatPrice
from gui.shared.money import Money
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from messenger.formatters.service_channel import QuestAchievesFormatter
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.gui.system_messages import ISystemMessages

def pushReRollSuccessNotification(currency, rollPrice):
    systemMessages = dependency.instance(ISystemMessages)
    price = Money.makeFrom(currency, rollPrice)
    textPrice = formatPrice(price, useIcon=True, useStyle=True, reverse=True)
    systemMessages.proto.serviceChannel.pushClientMessage(message=backport.text(R.strings.event.notifications.reroll.body(), price=textPrice), msgType=SCH_CLIENT_MSG_TYPE.REROLL_LOOTBOX, auxData=[SystemMessages.SM_TYPE.WtEventReRoll.name(),
     NotificationPriorityLevel.MEDIUM,
     {'header': backport.text(R.strings.event.notifications.reroll.header())},
     currency + 'Icon'])


def pushReRollFailedNotification():
    SystemMessages.pushMessage(text=backport.text(R.strings.event.notifications.reroll.error()), priority=NotificationPriorityLevel.MEDIUM, type=SystemMessages.SM_TYPE.Error)


def pushOpenedLootBoxNotification():
    SystemMessages.pushMessage(text='', priority=NotificationPriorityLevel.HIGH, type=SystemMessages.SM_TYPE.WtEventOpenedBox)


def pushLootBoxRewardsNotification(rewards):
    fmt = QuestAchievesFormatter.formatQuestAchieves(getMergedBonusesFromDicts(rewards), False)
    if fmt is not None:
        SystemMessages.pushMessage(fmt, SystemMessages.SM_TYPE.LootBoxRewards)
    return
