# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/lobby/__init__.py
from frameworks.wulf import ViewFlags
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings, getSwfExtensionUrl
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.EVENT_BATTLES_ALIASES import EVENT_BATTLES_ALIASES
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.daapi.view.meta.WTEventEntryPointMeta import WTEventEntryPointMeta
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from white_tiger.gui.impl.lobby.entry_point.wt_banner_entry_point import WTEventEntryPoint
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings
from white_tiger_queue import WhiteTigerQueue
__all__ = []

class WTEventBattlesEntryPoint(WTEventEntryPointMeta):

    def _makeInjectView(self):
        return WTEventEntryPoint(flags=ViewFlags.VIEW)


def getContextMenuHandlers():
    pass


def getViewSettings():
    from white_tiger.gui.impl.lobby.wt_crew_view import WTEventCrewWidget
    from white_tiger.gui.impl.lobby.wt_carousel_view import WTEventCarouselWidget
    from white_tiger.gui.impl.lobby.wt_header_widget_view import WTEventHeaderWidgetComponent
    from white_tiger.gui.impl.lobby.wt_loot_box_entry_point import WTEventLootBoxEntrancePointWidget
    from white_tiger.gui.impl.lobby.wt_characteristics_panel_view import WTEventCharacteristicsPanelWidget
    from white_tiger.gui.Scaleform.daapi.view.lobby.wt_event_prime_time_view import WTEventPrimeTimeView
    return (ComponentSettings(HANGAR_ALIASES.WT_EVENT_ENTRY_POINT, WTEventBattlesEntryPoint, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.EVENT_BATTLE_QUEUE, WhiteTigerQueue, getSwfExtensionUrl('white_tiger', 'WTBattleQueue.swf'), WindowLayer.SUB_VIEW, VIEW_ALIAS.EVENT_BATTLE_QUEUE, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(EVENT_BATTLES_ALIASES.EVENT_PRIME_TIME_VIEW, WTEventPrimeTimeView, getSwfExtensionUrl('white_tiger', 'WTPrimeTime.swf'), WindowLayer.TOP_SUB_VIEW, EVENT_BATTLES_ALIASES.EVENT_PRIME_TIME_VIEW, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),
     ComponentSettings(HANGAR_ALIASES.WHITE_TIGER_WIDGET, WTEventHeaderWidgetComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EVENT_CAROUSEL_WIDGET, WTEventCarouselWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EVENT_CREW_WIDGET, WTEventCrewWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.LOOTBOXES_WIDGET, WTEventLootBoxEntrancePointWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HANGAR_ALIASES.EVENT_PARAMS_WIDGET, WTEventCharacteristicsPanelWidget, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (WhiteTigerPackageBusinessHandler(),)


class WhiteTigerPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((EVENT_BATTLES_ALIASES.EVENT_PRIME_TIME_VIEW, self.loadViewByCtxEvent),)
        super(WhiteTigerPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
