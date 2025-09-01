# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/minimap/markers_components.py
from chat_commands_consts import MarkerType
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import MinimapMarkerComponent, StaticDeathZoneMinimapMarkerComponent
import SoundGroups
from gui.Scaleform.daapi.view.battle.epic.minimap import MINIMAP_SCALE_TYPES
from gui.Scaleform.daapi.view.battle.shared.minimap import settings

class CampMinimapMarkerComponent(MinimapMarkerComponent):

    @property
    def bcMarkerType(self):
        return MarkerType.TARGET_POINT_MARKER_TYPE

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


class MagnusMinimapMarkerComponent(CampMinimapMarkerComponent):

    def _setupMarker(self, gui, **kwargs):
        super(MagnusMinimapMarkerComponent, self)._setupMarker(gui)
        gui.setHasAnimation(self._componentID, False)


class BotSpawnNotificationMarkerComponent(MinimapMarkerComponent):
    _ANIMATION_NAME = 'firstEnemy'
    _GUI_PROPS_NAME = 'enemy'

    def _setupMarker(self, gui, **kwargs):
        super(BotSpawnNotificationMarkerComponent, self)._setupMarker(gui)
        gui.invoke(self.componentID, 'setVehicleInfo', '', '', '', self._GUI_PROPS_NAME, self._ANIMATION_NAME)
        SoundGroups.g_instance.playSound2D(settings.MINIMAP_ATTENTION_SOUND_ID)


class LSStaticDeathZoneMinimapMarkerComponent(StaticDeathZoneMinimapMarkerComponent):
    _MINIMAP_1M_IN_PX = 0.21

    def _setupMarker(self, gui, **kwargs):
        super(LSStaticDeathZoneMinimapMarkerComponent, self)._setupMarker(gui)
        gui.setEntryParameters(self._componentID, doClip=False, scaleType=MINIMAP_SCALE_TYPES.REAL_SCALE)

    def _getSize(self):
        xc = yc = self._MINIMAP_1M_IN_PX * 2
        return (xc, yc)
