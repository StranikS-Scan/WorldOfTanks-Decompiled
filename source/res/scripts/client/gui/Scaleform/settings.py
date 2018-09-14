# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/settings.py
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from shared_utils import CONST_CONTAINER

class ICONS_SIZES(CONST_CONTAINER):
    X80 = '80x80'
    X48 = '48x48'
    X24 = '24x24'


class BADGES_ICONS(CONST_CONTAINER):
    X80 = ICONS_SIZES.X80
    X48 = ICONS_SIZES.X48
    X24 = ICONS_SIZES.X24


def getBadgeIconPath(size, badgeID):
    return RES_ICONS.getBadgeIcon(size, badgeID)
