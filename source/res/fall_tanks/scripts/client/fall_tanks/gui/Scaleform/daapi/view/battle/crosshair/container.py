# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/crosshair/container.py
from gui.Scaleform.daapi.view.battle.shared.crosshair.container import CrosshairPanelContainer
from fall_tanks.gui.Scaleform.daapi.view.battle.crosshair import plugins

class FallTanksCrosshairPanelContainer(CrosshairPanelContainer):

    def _getPlugins(self):
        commonPlugins = super(FallTanksCrosshairPanelContainer, self)._getPlugins()
        return plugins.updatePlugins(commonPlugins)
