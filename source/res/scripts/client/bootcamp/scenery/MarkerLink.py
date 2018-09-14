# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/scenery/MarkerLink.py
import Math
import BattleReplay

class MarkerLink(object):

    def __init__(self, markerName):
        self.name = markerName
        self.markerParams = None
        self.mm = None
        self.visible = True
        return

    def resolve(self, markerManager):
        self.markerManager = markerManager
        self.markerParams = self.markerManager.getMarkerParams(self.name)

    def show(self):
        if self.markerManager is not None and not self.visible:
            self.visible = True
            if not BattleReplay.g_replayCtrl.isPlaying:
                self.markerManager.showMarker(self.name)
        return

    def hide(self, silently=False):
        if self.markerManager is not None and self.visible:
            self.visible = False
            if not BattleReplay.g_replayCtrl.isPlaying:
                self.markerManager.hideMarker(self.name, silently)
        return

    position = property(lambda self: self.markerParams['position'] if self.markerParams is not None else Math.Vector3(0.0, 0.0, 0.0))
    isVisible = property(lambda self: self.visible)
