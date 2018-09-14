# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ViewSettings
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowDialogEvent

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


def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.cyberSport.CyberSportMainWindow import CyberSportMainWindow
    from gui.Scaleform.daapi.view.lobby.cyberSport.CyberSportIntroView import CyberSportIntroView
    from gui.Scaleform.daapi.view.lobby.cyberSport.CyberSportUnitsListView import CyberSportUnitsListView
    from gui.Scaleform.daapi.view.lobby.cyberSport.CyberSportUnitView import CyberSportUnitView
    from gui.Scaleform.daapi.view.dialogs.CyberSportDialog import CyberSportDialog
    from gui.Scaleform.daapi.view.lobby.cyberSport.RosterSlotSettingsWindow import RosterSlotSettingsWindow
    from gui.Scaleform.daapi.view.lobby.cyberSport.VehicleSelectorPopup import VehicleSelectorPopup
    return (GroupedViewSettings(CYBER_SPORT_ALIASES.CYBER_SPORT_WINDOW_PY, CyberSportMainWindow, CYBER_SPORT_ALIASES.CYBER_SPORT_WINDOW_UI, ViewTypes.WINDOW, '', CYBER_SPORT_ALIASES.CYBER_SPORT_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_PY, RosterSlotSettingsWindow, CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_UI, ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(CYBER_SPORT_ALIASES.VEHICLE_SELECTOR_POPUP_PY, VehicleSelectorPopup, CYBER_SPORT_ALIASES.VEHICLE_SELECTOR_POPUP_UI, ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(CYBER_SPORT_ALIASES.CYBER_SPORT_DIALOG_PY, CyberSportDialog, CYBER_SPORT_ALIASES.CYBER_SPORT_DIALOG_UI, ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DYNAMIC_SCOPE, True),
     ViewSettings(CYBER_SPORT_ALIASES.INTRO_VIEW_PY, CyberSportIntroView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CYBER_SPORT_ALIASES.UNITS_LIST_VIEW_PY, CyberSportUnitsListView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CYBER_SPORT_ALIASES.UNIT_VIEW_PY, CyberSportUnitView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_CyberSportBusinessHandler(), _CyberSportDialogsHandler())


class _CyberSportBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((CYBER_SPORT_ALIASES.CYBER_SPORT_WINDOW_PY, self.loadViewByCtxEvent), (CYBER_SPORT_ALIASES.VEHICLE_SELECTOR_POPUP_PY, self.loadViewByCtxEvent), (CYBER_SPORT_ALIASES.ROSTER_SLOT_SETTINGS_WINDOW_PY, self.loadViewByCtxEvent))
        super(_CyberSportBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)


class _CyberSportDialogsHandler(PackageBusinessHandler):

    def __init__(self):
        super(_CyberSportDialogsHandler, self).__init__(((ShowDialogEvent.SHOW_CYBER_SPORT_DIALOG, self.__showCyberSportDialog),), APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.DEFAULT)

    def __showCyberSportDialog(self, event):
        self.loadViewWithGenName(CYBER_SPORT_ALIASES.CYBER_SPORT_DIALOG_PY, event.meta, event.handler)
