# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vse_hud_settings_ctrl/settings/minimap.py


class MinimapClientModel(object):
    __slots__ = ('showGrid', 'minimumAnimationDuration', 'maximumAnimationDuration', 'animationDurationPerMeter', 'minimumAnimationDistance', 'canToggleFullMap')

    def __init__(self, showGrid, canToggleFullMap, minimumAnimationDuration, maximumAnimationDuration, animationDurationPerMeter, minimumAnimationDistance):
        super(MinimapClientModel, self).__init__()
        self.showGrid = showGrid
        self.canToggleFullMap = canToggleFullMap
        self.minimumAnimationDuration = minimumAnimationDuration
        self.maximumAnimationDuration = maximumAnimationDuration
        self.animationDurationPerMeter = animationDurationPerMeter
        self.minimumAnimationDistance = minimumAnimationDistance

    def __repr__(self):
        return ('<MinimapClientModel>: showGrid=%s, minimumAnimationDuration=%s, maximumAnimationDuration=%s, ' + 'animationDurationPerMeter=%s, minimumAnimationDistance=%s, canToggleFullMap=%s') % (self.showGrid,
         self.minimumAnimationDuration,
         self.maximumAnimationDuration,
         self.animationDurationPerMeter,
         self.minimumAnimationDistance,
         self.canToggleFullMap)
