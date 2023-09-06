# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/crosshair.py
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.shared.crosshair.plugins import AmmoPlugin

class StoryModeAmmoPlugin(AmmoPlugin):

    def _isInfinity(self):
        return True


class StoryModeCrosshairPanelContainer(CrosshairPanelContainer):

    def _getPlugins(self):
        plugins = super(StoryModeCrosshairPanelContainer, self)._getPlugins()
        plugins['ammo'] = StoryModeAmmoPlugin
        return plugins
