# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/minimap/markers_components.py
from __future__ import absolute_import
import BigWorld
from chat_commands_consts import MarkerType
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import MinimapMarkerComponent, StaticDeathZoneMinimapMarkerComponent
from halloween.gui.halloween_gui_constants import BATTLE_CTRL_ID
import SoundGroups
from gui.Scaleform.daapi.view.battle.epic.minimap import MINIMAP_SCALE_TYPES
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from helpers import dependency
from halloween.gui.halloween_gui_constants import SoulsCollectorMarkerStates
from skeletons.gui.battle_session import IBattleSessionProvider
from HWDeathZone import HWDeathZone

def getSoulsCollectorMinimapMarkerState(isFull, isCampActivated):
    if isCampActivated:
        if isFull:
            return SoulsCollectorMarkerStates.MOVE_TO_SOULS_COLLECTOR.value
        return SoulsCollectorMarkerStates.NOT_ENOUGHT_SOULS.value
    return SoulsCollectorMarkerStates.MOVE_TO_SOULS_COLLECTOR_CAMP_ACTIVE.value if isFull else SoulsCollectorMarkerStates.NOT_ENOUGHT_SOULS_CAMP_ACTIVE.value


class CampMinimapMarkerComponent(MinimapMarkerComponent):

    @property
    def bcMarkerType(self):
        return MarkerType.TARGET_POINT_MARKER_TYPE

    @classmethod
    def configReader(cls, section):
        config = super(CampMinimapMarkerComponent, cls).configReader(section)
        config.update({'shape': section.readString('shape', '')})
        return config

    def _createMarker(self, **kwargs):
        gui = self._gui()
        if gui and not self._isMarkerExists:
            matrix = self._translationOnlyMP if self._onlyTranslation else self._matrixProduct.a
            self._isMarkerExists = gui.createMarker(self._componentID, self._config['symbol'], self._config['container'], matrix=matrix, active=self._isVisible, targetID=self._targetID, bcMarkerType=self.bcMarkerType)
            if self._isMarkerExists:
                self._setupMarker(gui)

    def _setupMarker(self, gui, **kwargs):
        super(CampMinimapMarkerComponent, self)._setupMarker(gui)
        gui.setHasAnimation(self._componentID, True)
        gui.setEntryParameters(self._componentID, doClip=False, scaleType=MINIMAP_SCALE_TYPES.PROPORTIONAL)
        if self._config['shape']:
            gui.invoke(self.componentID, 'setIcon', self._config['shape'])


class SoulsCollectorMinimapMarkerComponent(CampMinimapMarkerComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    @property
    def hwBattleGuiCtrl(self):
        return self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    def _deleteMarker(self):
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onSoulCollectorProgress -= self._updateMarkerState
        super(SoulsCollectorMinimapMarkerComponent, self)._deleteMarker()

    def _setupMarker(self, gui, **kwargs):
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onSoulCollectorProgress += self._updateMarkerState
        gui.setEntryParameters(self._componentID, doClip=False, scaleType=MINIMAP_SCALE_TYPES.PROPORTIONAL)
        if self._entity and 'hwSoulsCollector' in self._entity.dynamicComponents:
            soulsComponent = self._entity.hwSoulsCollector
            self._updateMarkerState(soulsComponent.collected, soulsComponent.capacity, soulsComponent.isFull, soulsComponent.isCampActivated)

    def _updateMarkerState(self, collected, capacity, isFull, isCampActivated):
        gui = self._gui()
        if gui and self._isMarkerExists:
            gui.invoke(self.componentID, 'setVolotState', getSoulsCollectorMinimapMarkerState(isFull, isCampActivated))


class BotSpawnNotificationMarkerComponent(MinimapMarkerComponent):
    _ANIMATION_NAME = 'firstEnemy'
    _GUI_PROPS_NAME = 'enemy'

    def _setupMarker(self, gui, **kwargs):
        super(BotSpawnNotificationMarkerComponent, self)._setupMarker(gui)
        gui.invoke(self.componentID, 'setVehicleInfo', '', '', '', self._GUI_PROPS_NAME, self._ANIMATION_NAME)
        SoundGroups.g_instance.playSound2D(settings.MINIMAP_ATTENTION_SOUND_ID)


class HWStaticDeathZoneMinimapMarkerComponent(StaticDeathZoneMinimapMarkerComponent):
    _MINIMAP_1M_IN_PX = 0.21

    def _setupMarker(self, gui, **kwargs):
        super(HWStaticDeathZoneMinimapMarkerComponent, self)._setupMarker(gui)
        gui.setEntryParameters(self._componentID, doClip=False, scaleType=MINIMAP_SCALE_TYPES.REAL_SCALE)

    def _getSize(self):
        xc = yc = self._MINIMAP_1M_IN_PX * 2
        return (xc, yc)


class HWResizableDeathZoneMinimapMarkerComponent(HWStaticDeathZoneMinimapMarkerComponent):

    def _setupMarker(self, gui, **kwargs):
        self.setMarkerPosition(self._entity.position)
        super(HWResizableDeathZoneMinimapMarkerComponent, self)._setupMarker(gui, **kwargs)
        HWDeathZone.onResizeDeathZone += self._resize

    def detachGUI(self):
        HWDeathZone.onResizeDeathZone -= self._resize
        super(HWResizableDeathZoneMinimapMarkerComponent, self).detachGUI()

    def _fillMaskingPolygons(self, mask, xc, yc):
        polygon = super(HWResizableDeathZoneMinimapMarkerComponent, self).getPolygon()
        delta = self._entity.position - self.position
        self._maskingPolygons.append(sum(([(p[0] + delta[0]) * xc, (p[1] - delta[2]) * yc] for p in polygon), []))

    def getPolygon(self):
        boundingBox = BigWorld.player().arena.arenaType.boundingBox
        arenaHalfSize = (boundingBox[1] - boundingBox[0]) * 0.5
        arenaCenter = boundingBox[0] + (boundingBox[1] - boundingBox[0]) * 0.5
        delta = arenaCenter - (self._entity.position.x, self._entity.position.z)
        return [(-arenaHalfSize[0] + delta[0], arenaHalfSize[1] - delta[1]),
         (-arenaHalfSize[0] + delta[0], -arenaHalfSize[1] - delta[1]),
         (arenaHalfSize[0] + delta[0], -arenaHalfSize[1] - delta[1]),
         (arenaHalfSize[0] + delta[0], arenaHalfSize[1] - delta[1])]

    def _resize(self, zone):
        if zone.id != self._entity.id:
            return
        self.setMarkerPosition(self._entity.position)
        self._maskingPolygons = []
        polygon = self.getPolygon()
        xc, yc = self._getSize()
        self._polygon = sum(([p[0] * xc, p[1] * yc] for p in polygon), [])
        for mask in self._entity.masks:
            self._fillMaskingPolygons(mask, xc, yc)

        self._gui().invoke(self._componentID, 'clearZones')
        self._updatePolygon()

    def _updateMasks(self):
        visual = self._entity.visual
        if visual and self._entity.visual.isCircular:
            self._gui().invoke(self._componentID, 'addCircleZone', 0, 0, self._entity.zoneSize[0] * 0.5 * self._getSize()[0])
        else:
            for polygon in self._maskingPolygons:
                self._gui().invoke(self._componentID, 'addZoneData', polygon)
