# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/badges.py
from gui.doc_loaders.badges_loader import getAvailableBadges
from helpers import dependency
from skeletons.gui.shared.gui_items import IGuiItemsFactory

def buildBadge(badgeID, extraData=None):
    if badgeID != 0:
        allBadges = getAvailableBadges()
        badgeDescriptor = allBadges[badgeID].copy()
        if badgeDescriptor is not None:
            return dependency.instance(IGuiItemsFactory).createBadge(badgeDescriptor, extraData=extraData)
    return
