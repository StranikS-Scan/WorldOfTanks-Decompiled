# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_battles/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ScopeTemplates, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.EVENT_BATTLES_ALIASES import EVENT_BATTLES_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared.event_bus import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.event_battles.wt_event_prime_time_view import WTEventPrimeTimeView
    return (ViewSettings(EVENT_BATTLES_ALIASES.EVENT_PRIME_TIME_VIEW, WTEventPrimeTimeView, HANGAR_ALIASES.WT_EVENT_PRIME_TIME, WindowLayer.TOP_SUB_VIEW, EVENT_BATTLES_ALIASES.EVENT_PRIME_TIME_VIEW, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),)


def getBusinessHandlers():
    return (EventPackageBusinessHandler(),)


class EventPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((EVENT_BATTLES_ALIASES.EVENT_PRIME_TIME_VIEW, self.loadViewByCtxEvent),)
        super(EventPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
