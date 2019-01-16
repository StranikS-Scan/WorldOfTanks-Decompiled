# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/prb_helpers.py
from gui.Scaleform.settings import getBadgeIconPathByDimension
from gui.shared.formatters.icons import makeImageTag
from gui.shared.gui_items.badge import BadgeLayouts
from helpers import dependency
from skeletons.gui.shared import IItemsCache

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _findFirstPrefixBadge(selectedBadges, itemsCache=None):
    badgeDescrs = itemsCache.items.badges.available
    for sbID in selectedBadges:
        badgeDescr = badgeDescrs.get(sbID)
        if badgeDescr and badgeDescr['layout'] == BadgeLayouts.PREFIX:
            return sbID


class BadgesHelper(object):

    def __init__(self, badges=None):
        self.__badges = badges or []
        self.__prefixBadgeID = None
        return

    def getBadgeID(self):
        if self.__prefixBadgeID is None:
            self.__prefixBadgeID = _findFirstPrefixBadge(self.__badges)
        return self.__prefixBadgeID

    def getBadgeImgStr(self, size, vspace):
        badgeID = self.getBadgeID()
        return makeImageTag(getBadgeIconPathByDimension(size, badgeID), size, size, vspace) if badgeID else ''
