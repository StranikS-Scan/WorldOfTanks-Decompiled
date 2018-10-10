# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/prb_helpers.py
from gui.Scaleform.settings import getBadgeIconPathByDimension
from gui.shared.formatters.icons import makeImageTag
from shared_utils import first

class BadgesHelper(object):

    def __init__(self, badges=None):
        self.__badges = badges or []

    def getBadgeID(self):
        return first(self.__badges, 0)

    def getBadgeImgStr(self, size, vspace):
        badgeID = first(self.__badges, None)
        badgeImgStr = ''
        if badgeID is not None:
            badgeImgStr = makeImageTag(getBadgeIconPathByDimension(size, badgeID), size, size, vspace)
        return badgeImgStr
