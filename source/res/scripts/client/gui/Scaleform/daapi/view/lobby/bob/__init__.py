# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/bob/__init__.py
from gui.Scaleform.framework import WindowLayer, ScopeTemplates, ViewSettings, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_OF_BLOGGERS_ALIASES import BATTLE_OF_BLOGGERS_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.bob.bob_prime_time_view import BobPrimeTimeView
    from gui.Scaleform.daapi.view.lobby.bob.bob_modifiers_panel import BobModifiersPanelInject
    from gui.Scaleform.daapi.view.lobby.bob.bob_vehicle_parameters import BobVehicleParameters
    return (ViewSettings(BATTLE_OF_BLOGGERS_ALIASES.BOB_PRIME_TIME_ALIAS, BobPrimeTimeView, HANGAR_ALIASES.RANKED_PRIME_TIME, WindowLayer.SUB_VIEW, BATTLE_OF_BLOGGERS_ALIASES.BOB_PRIME_TIME_ALIAS, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True), ComponentSettings(HANGAR_ALIASES.BOB_MODIFIERS_PANEL, BobModifiersPanelInject, ScopeTemplates.DEFAULT_SCOPE), ComponentSettings(HANGAR_ALIASES.BOB_VEHICLE_PARAMETERS, BobVehicleParameters, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BobPackageBusinessHandler(),)


class BobPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((BATTLE_OF_BLOGGERS_ALIASES.BOB_PRIME_TIME_ALIAS, self.loadViewByCtxEvent),)
        super(BobPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
