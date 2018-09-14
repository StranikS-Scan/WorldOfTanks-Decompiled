# Embedded file name: scripts/client/notification/settings.py
LIST_SCROLL_STEP_FACTOR = 10
DEF_ICON_PATH = '../maps/icons/library/{0:>s}-1.png'

class NOTIFICATION_STATE(object):
    POPUPS = 0
    LIST = 1


class NOTIFICATION_TYPE(object):
    UNDEFINED = 0
    MESSAGE = 1
    INVITE = 2
    FRIENDSHIP_RQ = 3
    WGNC_POP_UP = 4
    CLUB_INVITE = 5
    CLUB_APPS = 6
    RANGE = (MESSAGE,
     INVITE,
     FRIENDSHIP_RQ,
     WGNC_POP_UP,
     CLUB_INVITE,
     CLUB_APPS)


ITEMS_MAX_LENGTHS = {NOTIFICATION_TYPE.MESSAGE: 250,
 NOTIFICATION_TYPE.INVITE: 100,
 NOTIFICATION_TYPE.FRIENDSHIP_RQ: 100,
 NOTIFICATION_TYPE.CLUB_INVITE: 100,
 NOTIFICATION_TYPE.CLUB_APPS: 1,
 NOTIFICATION_TYPE.WGNC_POP_UP: 500}

class NOTIFICATION_BUTTON_STATE(object):
    HIDDEN = 0
    VISIBLE = 1
    ENABLED = 2
    DEFAULT = VISIBLE | ENABLED


class LAYOUT_PADDING(object):
    HANGAR = (4, 235)
    OTHER = (0, 35)
    LIST = (45, 34)


def makePathToIcon(iconName):
    result = ''
    if iconName and len(iconName):
        result = DEF_ICON_PATH.format(iconName)
    return result
