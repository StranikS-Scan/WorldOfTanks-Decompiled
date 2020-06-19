# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/spg_event/__init__.py
from gui.Scaleform.daapi.view.lobby.spg_event.prime_time_view import SPGEventPrimeTimeView
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework import ViewSettings, ViewTypes
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.EVENT10YC_ALIASES import EVENT10YC_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
    return (ViewSettings(EVENT10YC_ALIASES.EVENT_10YC_PRIME_TIME_ALIAS, SPGEventPrimeTimeView, HANGAR_ALIASES.EVENT_10YC_PRIME_TIME, ViewTypes.LOBBY_SUB, EVENT10YC_ALIASES.EVENT_10YC_PRIME_TIME_ALIAS, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),)


def getBusinessHandlers():
    return (SPGBattlesPackageBusinessHandler(),)


class SPGBattlesPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((EVENT10YC_ALIASES.EVENT_10YC_PRIME_TIME_ALIAS, self.loadViewByCtxEvent),)
        super(SPGBattlesPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
