# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/mini_map_background.py
from typing import TYPE_CHECKING, Optional
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.minimap.common import EntriesPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.component import getMapImagePath
from MapImageComponent import MapImageComponent
if TYPE_CHECKING:
    from ClientArena import ClientArena

class MiniMapBackground(EntriesPlugin):
    _MMAPS_PATH_FORMAT = 'img://spaces/{}/additional/{}.dds'

    def start(self):
        super(MiniMapBackground, self).start()
        MapImageComponent.onMapUpdate += self.__updateMiniMapBackground
        self.__updateMiniMapBackground()

    def fini(self):
        MapImageComponent.onMapUpdate -= self.__updateMiniMapBackground
        super(MiniMapBackground, self).fini()

    def __updateMiniMapBackground(self):
        if not self._parentObj:
            return
        path = self.__getMinimapPath()
        if not path:
            return
        self._parentObj.as_setBackgroundS(path)

    def __getMinimapPath(self):
        arena = BigWorld.player().arena
        geometryName = arena.arenaType.geometryName
        if geometryName:
            mapImage = arena.arenaInfo.mapImageComponent.mapImage
            if mapImage:
                return self._MMAPS_PATH_FORMAT.format(geometryName, mapImage)
        return getMapImagePath(arena.arenaType.minimap)
