# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/birthday_helpers/__init__.py
from gui.Scaleform.locale.MENU import MENU
from helpers import i18n, dependency
from skeletons.gui.shared import IItemsCache
from mt_birthday.birthday_constants import POST_BATTLE_EXTRA_TAB_UI
_extraTabBlock = {'label': i18n.makeString(MENU.FINALSTATISTIC_TABS_POSTBATTLEEXTRATAB),
 'linkage': POST_BATTLE_EXTRA_TAB_UI,
 'viewId': POST_BATTLE_EXTRA_TAB_UI,
 'showWndBg': True}

def addExtraPostBattleTab(tabs):
    tabs.getMeta().addMeta(_extraTabBlock)


def deleteExtraTab(tabs):
    tabs.getMeta().popMeta(_extraTabBlock)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getLootBoxByID(lootboxID, itemsCache=None):
    lb = itemsCache.items.tokens.getLootBoxByID(lootboxID)
    return lb if lb and lb.isVisible() else None
