# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/__init__.py
__all___ = ('CyberSportIntroView', 'CyberSportMainWindow', 'CyberSportUnitsListView', 'CyberSportUnitView')

class PLAYER_GUI_STATUS(object):
    NORMAL = 0
    READY = 2
    BATTLE = 3
    LOCKED = 4
    CREATOR = 5


class SLOT_LABEL(object):
    DEFAULT = ''
    LOCKED = 'freezed'
    CLOSED = 'locked'
    NOT_AVAILABLE = 'notAvailable'
    EMPTY = 'emptySlot'
