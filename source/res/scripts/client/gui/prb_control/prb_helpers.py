# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/prb_helpers.py
from gui.Scaleform.settings import getBadgeIconPathByDimension
from gui.shared.formatters.icons import makeImageTag
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.shared import IItemsCache

class BadgesHelper(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, badges=None):
        self.__badges = badges or []

    def getBadgeID(self):
        return self.__findFirstPrefixBadge(0)

    def getBadgeImgStr(self, size, vspace):
        badgeID = self.__findFirstPrefixBadge()
        badgeImgStr = ''
        if badgeID is not None:
            badgeImgStr = makeImageTag(getBadgeIconPathByDimension(size, badgeID), size, size, vspace)
        return badgeImgStr

    def __findFirstPrefixBadge(self, default=None):

        def __isPrefixBadge(badgeID):
            badge = self.itemsCache.items.getBadges().get(badgeID)
            return badge.isPrefixLayout() if badge else False

        return findFirst(__isPrefixBadge, self.__badges, default)
