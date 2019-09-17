# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FestivalRaceMinimapMeta.py
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent

class FestivalRaceMinimapMeta(ClassicMinimapComponent):

    def as_setPositionS(self, currentPosition, totalPlayersAmount):
        return self.flashObject.as_setPosition(currentPosition, totalPlayersAmount) if self._isDAAPIInited() else None
