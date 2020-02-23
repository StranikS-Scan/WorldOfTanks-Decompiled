# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/prb_helpers.py
from gui.shared.badges import buildBadge
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
        self.__badgesRawData = badges or ()
        self.__badges = {}
        self.__prefixBadgeID = None
        return

    def getBadge(self):
        badgeID = self.__getBadgeID()
        if badgeID <= 0:
            return None
        else:
            if badgeID not in self.__badges:
                self.__badges[badgeID] = buildBadge(badgeID, self.__getBadgeExtraInfo())
            return self.__badges[badgeID]

    def __getBadgeID(self):
        if self.__prefixBadgeID is None:
            self.__prefixBadgeID = _findFirstPrefixBadge(self.__getSelectedBadges())
        return self.__prefixBadgeID

    def __getSelectedBadges(self):
        return self.__badgesRawData[0]

    def __getBadgeExtraInfo(self):
        return self.__badgesRawData[1]
