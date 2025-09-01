# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/shared/crosshair/container.py
from gui.Scaleform.daapi.view.battle.shared.crosshair.container import CrosshairPanelContainer
from last_stand.gui.scaleform.daapi.view.battle.shared.crosshair import plugins

class LSCrosshairPanelContainer(CrosshairPanelContainer):

    def _getPlugins(self):
        res = super(LSCrosshairPanelContainer, self)._getPlugins()
        res['vehicleState'] = plugins.LSVehicleStatePlugin
        return res
