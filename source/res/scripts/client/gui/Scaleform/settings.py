# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/settings.py
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from shared_utils import CONST_CONTAINER

class TOOLTIP_TYPES(object):
    COMPLEX = 'complex'
    SPECIAL = 'special'
    WULF = 'wulf'
    NONE = 'none'


class ICONS_SIZES(CONST_CONTAINER):
    X550 = '550x550'
    X320 = '320x320'
    X220 = '220x220'
    X110 = '110x110'
    X80 = '80x80'
    X48 = '48x48'
    X32 = '32x32'
    X24 = '24x24'


class BADGES_ICONS(CONST_CONTAINER):
    X320 = ICONS_SIZES.X320
    X220 = ICONS_SIZES.X220
    X110 = ICONS_SIZES.X110
    X80 = ICONS_SIZES.X80
    X48 = ICONS_SIZES.X48
    X32 = ICONS_SIZES.X32
    X24 = ICONS_SIZES.X24


class BADGES_STRIPS_ICONS(CONST_CONTAINER):
    X100 = '100x40'
    X68 = '68x28'
    X64 = '64x24'


class BADGES_HIGHLIGHTS(CONST_CONTAINER):
    RED = 'red'
    VIOLET = 'violet'
    GREEN = 'green'
    GOLD = 'gold'


def getBadgeIconPath(size, badgeID):
    return RES_ICONS.getBadgeIcon(size, badgeID)


def getAwardBadgeIconPath(size, badgeID):
    return RES_ICONS.getAwardBadgeIcon(size, badgeID)


def getBadgeHighlightIconPath(value):
    return RES_ICONS.getBadgeHighlightIcon(value)


def getPersonalMissionVehicleAwardImage(size, vehicleName):
    return RES_ICONS.getPersonalMissionVehicleAwardImage(size, vehicleName)
