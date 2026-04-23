# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory/gui/window_events.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl.gen import R
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.impl import IGuiLoader
_OVERLAPPING_ALIASES = (VIEW_ALIAS.VEHICLE_PREVIEW,)

def showMuseumVehicleView():
    if _closeOtherViews():
        nextTick(_loadMuseumView)()
        return
    _loadMuseumView()


def _closeOtherViews():

    def _predicate(w):
        layer = getattr(w, 'layer', None)
        content = getattr(w, 'content', None)
        alias = getattr(content, 'alias', None)
        return layer == WindowLayer.SUB_VIEW and (alias in _OVERLAPPING_ALIASES or isinstance(content, VehiclePreview))

    uiLoader = dependency.instance(IGuiLoader)
    subViews = uiLoader.windowsManager.findWindows(_predicate)
    for view in subViews:
        view.destroy()

    return bool(subViews)


def _loadMuseumView():
    from museum_of_glory.gui.impl.lobby.feature.museum_vehicle_view import MuseumVehicleView
    uiLoader = dependency.instance(IGuiLoader)
    layoutID = R.views.museum_of_glory.lobby.feature.MuseumVehicleView()
    if uiLoader.windowsManager.getViewByLayoutID(layoutID) is None:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=layoutID, viewClass=MuseumVehicleView, scope=ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
    return
