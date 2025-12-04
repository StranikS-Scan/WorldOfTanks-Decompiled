# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/shared/formatters.py
import typing
from constants import LOOTBOX_TOKEN_PREFIX
from gui.shared.formatters import text_styles
from items.tankmen import RECRUIT_TMAN_TOKEN_PREFIX
from new_year.gui.bonuses.bonuses_packers import packBonuses
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.server_events.recruit_helper import getRecruitInfo
ITEMS_FORMATTER = "<font color='#F2F2F7'>{} x{}</font>"
ITEMS_WO_COUNT_FORMATTER = "<font color='#F2F2F7'>{}</font>"

def formatPurchaseItems(items, packer=None, skipCount=False):
    formattedItems = []
    for bonus in packBonuses(items, packer):
        count = bonus.getValue() or 1
        label = bonus.getLabel()
        backportText = R.strings.ny.notifications.reward.product()
        if bonus.getName() == 'dossier_badge':
            formattedItems.append(backport.text(backportText, product=ITEMS_WO_COUNT_FORMATTER.format(label)))
        formattedItems.append(backport.text(backportText, product=ITEMS_FORMATTER.format(label, count)))

    return ', '.join(formattedItems)


ITEM_VALUE_FORMAT = text_styles.tutorial('x{}')

def formatPurchasedItems(items):
    formattedItems = []
    for name, count in items.iteritems():
        backportText = R.strings.ny.notification.racoon.purchased.item.dyn(name)()
        formattedItems.append(backport.text(backportText, text=ITEM_VALUE_FORMAT.format(count)))

    return '<br/><br/>'.join(formattedItems)


def formatActivatedItem(name, count, progressPoints, leaderPoint):
    formattedItems = []
    subHeaderText = R.strings.ny.notification.racoon.activated.subHeader.dyn(name)()
    formattedItems.append(backport.text(subHeaderText, count=ITEM_VALUE_FORMAT.format(int(count))))
    progressText = R.strings.ny.notification.racoon.activated.progressPoints()
    formattedItems.append(backport.text(progressText, count=text_styles.vehicleName(str(int(progressPoints)))))
    if leaderPoint:
        leaderText = R.strings.ny.notification.racoon.activated.leaderPoints()
        formattedItems.append(backport.text(leaderText, count=text_styles.vehicleName(str(int(leaderPoint)))))
    return '<br/><br/>'.join(formattedItems)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def formatMailRewardsItems(data, itemsCache=None):
    rewards = []
    tokens = data.get('tokens', {})
    for name, token in tokens.iteritems():
        if name.startswith(LOOTBOX_TOKEN_PREFIX):
            lootBox = itemsCache.items.tokens.getLootBoxByTokenID(name)
            if lootBox is not None:
                rewards.append(backport.text(R.strings.ny.notification.racoon.gift.reward.lootbox.dyn(lootBox.getIconName())(), count=text_styles.vehicleName(str(token.get('count', 0)))))
        if name.startswith(RECRUIT_TMAN_TOKEN_PREFIX):
            recruitInfo = getRecruitInfo(name)
            if recruitInfo is None:
                continue
            name = recruitInfo.getFullUserName()
            rewards.append(backport.text(R.strings.ny.notification.racoon.gift.reward.tman(), tmanName=name, count=text_styles.vehicleName(str(token.get('count', 0)))))

    return '<br/>'.join(rewards)
