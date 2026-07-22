# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/birthday_helpers/__init__.py
from helpers import dependency
from skeletons.gui.shared import IItemsCache

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getLootBoxByID(lootboxID, itemsCache=None):
    lb = itemsCache.items.tokens.getLootBoxByID(lootboxID)
    return lb if lb and lb.isVisible() else None


def isBirthdayOrdinaryQuest(questID):
    return questID.startswith('mt_birthday_quest_giver:quests')
