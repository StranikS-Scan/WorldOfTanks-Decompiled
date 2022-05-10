# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/event_platform/gui/view/lobby/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.bootcamp import BCHangar
from gui.Scaleform.daapi.view.bootcamp.bootcamp_cm_handlers import BCVehicleContextMenuHandler
from gui.Scaleform.daapi.view.bootcamp.component_override import BootcampComponentOverride
from gui.Scaleform.framework import ScopeTemplates, ConditionalViewSettings
from event_platform.gui.impl.event_hangar import EventHangar
from event_platform.gui.impl.lobby_cm import EPVehicleContextMenuHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE

def getContextMenuHandlers():
    return ((CONTEXT_MENU_HANDLER_TYPE.VEHICLE, BootcampComponentOverride(EPVehicleContextMenuHandler, BCVehicleContextMenuHandler)),)


def getViewSettings():
    return (ConditionalViewSettings(VIEW_ALIAS.LOBBY_HANGAR, BootcampComponentOverride(EventHangar, BCHangar), 'hangar.swf', WindowLayer.SUB_VIEW, None, VIEW_ALIAS.LOBBY_HANGAR, ScopeTemplates.LOBBY_SUB_SCOPE),)


def getBusinessHandlers():
    pass
