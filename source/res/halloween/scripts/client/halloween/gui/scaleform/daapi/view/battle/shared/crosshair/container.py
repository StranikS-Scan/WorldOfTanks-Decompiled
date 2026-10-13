# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/shared/crosshair/container.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.battle.shared.crosshair.container import CrosshairPanelContainer
from halloween.gui.scaleform.daapi.view.battle.shared.crosshair import plugins

class HalloweenCrosshairPanelContainer(CrosshairPanelContainer):

    def _getPlugins(self):
        res = super(HalloweenCrosshairPanelContainer, self)._getPlugins()
        res['vehicleState'] = plugins.HWVehicleStatePlugin
        return res
