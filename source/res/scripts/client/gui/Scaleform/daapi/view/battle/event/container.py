# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/container.py
from gui.Scaleform.daapi.view.battle.event.crosshair import PveAmmoPlugin, PveSettingsPlugin, PveShotResultIndicatorPlugin
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer

class PveCrosshairPanelContainer(CrosshairPanelContainer):

    def __init__(self):
        plugins = {'settings': PveSettingsPlugin,
         'ammo': PveAmmoPlugin,
         'shotResultIndicator': PveShotResultIndicatorPlugin,
         'siegeMode': None}
        super(PveCrosshairPanelContainer, self).__init__(overridePlugins=plugins)
        return

    def setGunMarkerColor(self, markerType, color):
        return super(PveCrosshairPanelContainer, self).setGunMarkerColor(markerType, 'white')
