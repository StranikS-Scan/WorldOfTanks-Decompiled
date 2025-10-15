# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/Scaleform/daapi/view/battle/portal_minimap.py
from gui.Scaleform.daapi.view.battle.epic.minimap import EpicMinimapComponent
from portal.gui.Scaleform.daapi.view.battle.shared.markers.minimap import PortalMinimapAreaMarkersPlugin, PortalControlPointsPlugin, PortalMinimapPingPlugin

class PortalMinimapComponent(EpicMinimapComponent):
    __PORTAL_ZOOM_MODE = 2.0

    def _setupPlugins(self, visitor):
        setup = super(PortalMinimapComponent, self)._setupPlugins(visitor)
        setup['portal_minimap_markers'] = PortalMinimapAreaMarkersPlugin
        setup['points'] = PortalControlPointsPlugin
        setup['pinging'] = PortalMinimapPingPlugin
        return setup

    def _populate(self):
        super(PortalMinimapComponent, self)._populate()
        self.updateZoomMode(self.__PORTAL_ZOOM_MODE)
