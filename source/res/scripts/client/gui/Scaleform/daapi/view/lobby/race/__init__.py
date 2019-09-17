# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/race/__init__.py
from gui.Scaleform.daapi.view.lobby.race.commander_cmp import CommanderComponent
from gui.Scaleform.daapi.view.lobby.race.racing_widget_cmp import RacingWidgetComponent
from gui.Scaleform.daapi.view.lobby.race.tech_parameters_cmp import TechParametersComponent
from gui.Scaleform.daapi.view.lobby.race.hangar_bottom_panel_cmp import HangarBottomPanelComponent
from gui.Scaleform.framework import ViewTypes, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.FESTIVAL_RACE_ALIASES import FESTIVAL_RACE_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    return (ViewSettings(FESTIVAL_RACE_ALIASES.COMMANDER_COMPONENT, CommanderComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(FESTIVAL_RACE_ALIASES.TECH_PARAMETERS_COMPONENT, TechParametersComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(FESTIVAL_RACE_ALIASES.BOTTOM_PANEL_COMPONENT, HangarBottomPanelComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(FESTIVAL_RACE_ALIASES.WIDGET_COMPONENT, RacingWidgetComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.LOBBY_SUB_SCOPE))


def getBusinessHandlers():
    return (BattleRoyalePackageBusinessHandler(),)


class BattleRoyalePackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ()
        super(BattleRoyalePackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
