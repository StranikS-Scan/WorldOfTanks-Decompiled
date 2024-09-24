# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/shared/packers/bonus.py
import typing
from gui.server_events.awards_formatters import getDefaultFormattersMap, ItemsBonusFormatter
from gui.shared.missions.packers.bonus import ItemBonusUIPacker, BonusUIPacker, getDefaultBonusPackersMap
if typing.TYPE_CHECKING:
    from typing import Dict

def getSMFormattersMap():
    formattersMap = getDefaultFormattersMap()
    formattersMap['items'] = SMItemsBonusFormatter()
    return formattersMap


def getSMBonusPackersMap():
    bonusMap = getDefaultBonusPackersMap()
    bonusMap['items'] = SMItemBonusUIPacker()
    return bonusMap


def getSMBonusPacker():
    return BonusUIPacker(getSMBonusPackersMap())


class SMItemBonusUIPacker(ItemBonusUIPacker):

    @staticmethod
    def _itemsSortFunction(item):
        return -item[0].intCD


class SMItemsBonusFormatter(ItemsBonusFormatter):

    def _getItems(self, bonus):
        return sorted(bonus.getItems().items(), key=lambda i: -i[0].intCD)
