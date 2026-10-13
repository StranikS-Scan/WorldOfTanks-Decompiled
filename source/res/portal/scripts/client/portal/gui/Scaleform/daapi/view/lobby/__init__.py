# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/lobby/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.bootcamp.BCHangar import BCHangar
from gui.Scaleform.daapi.view.bootcamp.component_override import BootcampComponentOverride
from gui.Scaleform.framework import ScopeTemplates, ConditionalViewSettings, ComponentSettings, getSwfExtensionUrl
from gui.Scaleform.genConsts.HANGAR_CONSTS import HANGAR_CONSTS
from portal.gui.portal_gui_constants import VIEW_ALIAS
from portal.gui.Scaleform.daapi.view.lobby.portal_hangar import PortalHangar
from portal.gui.Scaleform.daapi.view.lobby.portal_banner_entry_point import PortalBannerEntryPoint
from portal_constants import PORTAL_BANNER_ENTRY_POINT
__all__ = ('PortalHangar',)

def getContextMenuHandlers():
    pass


def getViewSettings():
    from portal.gui.impl.lobby.portal_lobby_view import PortalLobby
    return (ComponentSettings(PORTAL_BANNER_ENTRY_POINT, PortalBannerEntryPoint, ScopeTemplates.DEFAULT_SCOPE), ComponentSettings(HANGAR_CONSTS.PORTAL_EVENT_MODIFIERS, PortalLobby, ScopeTemplates.LOBBY_SUB_SCOPE))


def getBusinessHandlers():
    pass
