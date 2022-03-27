# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rts_battles/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ScopeTemplates, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.RTSBATTLES_ALIASES import RTSBATTLES_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.rts_battles.rts_battle_prime_times import RtsBattlesPrimeTimeView
    from gui.Scaleform.daapi.view.lobby.rts_battles.rts_browser_pages import RTSInfoPageView
    return (ViewSettings(RTSBATTLES_ALIASES.RTS_BATTLES_PRIME_TIME, RtsBattlesPrimeTimeView, HANGAR_ALIASES.EPIC_PRIME_TIME, WindowLayer.SUB_VIEW, RTSBATTLES_ALIASES.RTS_BATTLES_PRIME_TIME, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True), ViewSettings(RTSBATTLES_ALIASES.RTS_BATTLES_INFO_PAGE, RTSInfoPageView, 'browserScreen.swf', WindowLayer.SUB_VIEW, RTSBATTLES_ALIASES.RTS_BATTLES_INFO_PAGE, ScopeTemplates.LOBBY_SUB_SCOPE, True))


def getBusinessHandlers():
    return (RtsBattlesPackageBusinessHandler(),)


class RtsBattlesPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((RTSBATTLES_ALIASES.RTS_BATTLES_PRIME_TIME, self.loadViewByCtxEvent), (RTSBATTLES_ALIASES.RTS_BATTLES_INFO_PAGE, self.loadViewByCtxEvent))
        super(RtsBattlesPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
