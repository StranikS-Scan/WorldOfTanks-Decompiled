# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/__init__.py
from frameworks.wulf import WindowLayer
from gui.shared import EVENT_BUS_SCOPE
from gui.app_loader import settings as app_settings
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings, GroupedViewSettings
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.fortifications.components.stronghold_battles_list_view import StrongholdBattlesListView
    from gui.Scaleform.daapi.view.lobby.fortifications.stronghold_battle_room import StrongholdBattleRoom
    from gui.Scaleform.daapi.view.lobby.fortifications.stronghold_battle_room_window import StrongholdBattleRoomWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.FortReserveSelectPopover import FortReserveSelectPopover
    from gui.Scaleform.daapi.view.lobby.fortifications.StrongholdSendInvitesWindow import StrongholdSendInvitesWindow
    from gui.Scaleform.daapi.view.lobby.fortifications.fort_vehicle_select_popover import FortVehicleSelectPopover
    return (GroupedViewSettings(FORTIFICATION_ALIASES.STRONGHOLD_SEND_INVITES_WINDOW_PY, StrongholdSendInvitesWindow, 'sendInvitesWindow.swf', WindowLayer.WINDOW, '', FORTIFICATION_ALIASES.STRONGHOLD_SEND_INVITES_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_RESERVE_SELECT_POPOVER_ALIAS, FortReserveSelectPopover, FORTIFICATION_ALIASES.FORT_FITTING_SELECT_POPOVER_UI, WindowLayer.WINDOW, FORTIFICATION_ALIASES.FORT_RESERVE_SELECT_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_RESERVE_SELECT_POPOVER_ALIAS, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.FORT_VEHICLE_SELECT_POPOVER_ALIAS, FortVehicleSelectPopover, FORTIFICATION_ALIASES.FORT_VEHICLE_SELECT_POPOVER_UI, WindowLayer.WINDOW, FORTIFICATION_ALIASES.FORT_VEHICLE_SELECT_POPOVER_ALIAS, FORTIFICATION_ALIASES.FORT_VEHICLE_SELECT_POPOVER_ALIAS, ScopeTemplates.WINDOW_VIEWED_MULTISCOPE),
     GroupedViewSettings(FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_WINDOW_ALIAS, StrongholdBattleRoomWindow, FORTIFICATION_ALIASES.FORT_BATTLE_ROOM_WINDOW_UI, WindowLayer.WINDOW, '', FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_WINDOW_ALIAS, ScopeTemplates.DEFAULT_SCOPE, True),
     ComponentSettings(FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_LIST_VIEW_PY, StrongholdBattlesListView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_VIEW_PY, StrongholdBattleRoom, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_FortsBusinessHandler(),)


class _FortsBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_WINDOW_ALIAS, self.__showStrongholdBattleRoomWindow),
         (FORTIFICATION_ALIASES.FORT_RESERVE_SELECT_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.FORT_VEHICLE_SELECT_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (FORTIFICATION_ALIASES.STRONGHOLD_SEND_INVITES_WINDOW_PY, self.__showPrebattleWindow))
        super(_FortsBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def __showStrongholdBattleRoomWindow(self, event):
        alias = name = FORTIFICATION_ALIASES.STRONGHOLD_BATTLE_ROOM_WINDOW_ALIAS
        window = self.findViewByAlias(WindowLayer.WINDOW, alias)
        if window is not None:
            if event.ctx.get('modeFlags') == FUNCTIONAL_FLAG.UNIT_BROWSER:
                window.onBrowseRallies()
        self.loadViewWithDefName(alias, name, None, event.ctx)
        return

    def __showPrebattleWindow(self, event):
        alias = name = event.alias
        self.loadViewWithDefName(alias, name, None, event.ctx)
        return
