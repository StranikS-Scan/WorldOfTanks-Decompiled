# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/crosshair/container.py
from __future__ import absolute_import
import typing
from fort_rush.gui.scaleform.daapi.view.battle.crosshair.plugins import createPlugins, SHOT_RESULT_INDICATOR
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
if typing.TYPE_CHECKING:
    from gui.shared.utils.plugins import IPlugin

class FortRushCrosshairPanelContainer(CrosshairPanelContainer):

    def __init__(self):
        super(FortRushCrosshairPanelContainer, self).__init__()
        self._addPlugins(createPlugins())

    def _getPlugins(self):
        enabledPlugins = super(FortRushCrosshairPanelContainer, self)._getPlugins()
        enabledPlugins.pop(SHOT_RESULT_INDICATOR)
        return enabledPlugins
