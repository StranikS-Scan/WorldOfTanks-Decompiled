# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/__init__.py
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.managers.context_menu import ContextMenuManager
__all___ = ('CyberSportIntroView', 'CyberSportMainWindow', 'CyberSportUnitsListView', 'CyberSportUnitView')
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.CLUB_STAFF, 'gui.Scaleform.daapi.view.lobby.cyberSport.ClubUserCMHandler', 'ClubUserCMHandler')

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
    NOT_ALLOWED = 'notAllowed'
    EMPTY = 'emptySlot'
    REQUIRED = 'required'
