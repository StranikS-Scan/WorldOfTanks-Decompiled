# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/markers_components.py
import BigWorld
import Math
import SoundGroups
import WWISE
from typing import TYPE_CHECKING
from StoryModeLootableComponent import StoryModeLootableComponent
from chat_commands_consts import MarkerType, INVALID_TARGET_ID
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import PolygonalZoneMinimapMarkerComponent, World2DLocationMarkerComponent, BaseMinimapMarkerComponent, ComponentBitMask
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import CONTAINER_NAME, ENTRY_SYMBOL_NAME, VIEW_RANGE_CIRCLES_AS3_DESCR, CIRCLE_STYLE
from gui.battle_control import minimap_utils
from gui.impl import backport
from gui.impl.gen import R
from helpers import time_utils, dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from story_mode.gui.sound_constants import VDAY_LOOT_CAPTURE_COMPLETE_SOUND, VDAY_LOOT_CAPTURE_PROGRESS_SOUND, VDAY_LOOT_CAPTURE_RTPC, VDAY_LOOT_CAPTURE_START_SOUND, VDAY_LOOT_CAPTURE_STOP_SOUND
from story_mode_common.story_mode_constants import RECON_ABILITY
if TYPE_CHECKING:
    import ResMgr
    from Math import Vector3
    from gui.Scaleform.daapi.view.battle.shared.minimap.component import MinimapComponent

class SMPolygonalZoneMinimapMarkerComponent(PolygonalZoneMinimapMarkerComponent):

    def _getSize(self):
        bottomLeft, topRight = BigWorld.player().arena.arenaType.boundingBox
        arenaSize = topRight - bottomLeft
        vSide, hSide = arenaSize
        if vSide > hSide:
            xc = minimap_utils.MINIMAP_SIZE[0] / vSide * 2
            yc = minimap_utils.MINIMAP_SIZE[1] / vSide * 2
        else:
            xc = minimap_utils.MINIMAP_SIZE[0] / hSide * 2
            yc = minimap_utils.MINIMAP_SIZE[1] / hSide * 2
        return (xc, yc)


class LootMarkerComponent(World2DLocationMarkerComponent):

    def __init__(self, config, matrixProduct, entity=None, targetID=INVALID_TARGET_ID, isVisible=True):
        super(LootMarkerComponent, self).__init__(config, matrixProduct, entity, targetID, isVisible)
        self._tickTimerId = None
        self._startTime = 0
        self._captureTime = 0
        return

    @classmethod
    def configReader(cls, section):
        config = super(LootMarkerComponent, cls).configReader(section)
        config.update({'loot_type': section.readString('loot_type')})
        return config

    @property
    def bcMarkerType(self):
        return MarkerType.NON_INTERACTIVE

    def _setupMarker(self, gui, **kwargs):
        super(LootMarkerComponent, self)._setupMarker(gui, **kwargs)
        lootType = self._config['loot_type']
        gui.invokeMarker(self.componentID, 'updateLootType', lootType, backport.text(R.strings.sm_battle.lootCapturing.dyn(lootType)()))
        if StoryModeLootableComponent.__name__ in self._entity.components:
            self._entity.StoryModeLootableComponent.onStartCapturing += self._onStartCapturing
            self._entity.StoryModeLootableComponent.onStopCapturing += self._onStopCapturing

    def _onStartCapturing(self, startTime, captureTime):
        gui = self._gui()
        if not gui:
            return
        gui.invokeMarker(self.componentID, 'updateLootingVisible', True)
        self._startTime = startTime
        self._captureTime = captureTime
        self._tick()
        SoundGroups.g_instance.playSound2D(VDAY_LOOT_CAPTURE_START_SOUND)
        WWISE.WW_setRTCPGlobal(VDAY_LOOT_CAPTURE_RTPC, 0)
        self._isStickyFromConfig = True
        gui.setMarkerSticky(self.componentID, True)

    def _tick(self):
        gui = self._gui()
        if not gui:
            return
        timeLeft = round(max(0, self._startTime + self._captureTime - BigWorld.serverTime()))
        gui.invokeMarker(self.componentID, 'updateLootingTime', time_utils.getTimeLeftFormat(timeLeft))
        self._tickTimerId = BigWorld.callback(1.0, self._tick)
        rtpcValue = round((1 - timeLeft / self._captureTime) * 100)
        if rtpcValue != 0:
            SoundGroups.g_instance.playSound2D(VDAY_LOOT_CAPTURE_PROGRESS_SOUND)
            WWISE.WW_setRTCPGlobal(VDAY_LOOT_CAPTURE_RTPC, rtpcValue)

    def _onStopCapturing(self):
        self._cancelTimer()
        gui = self._gui()
        if not gui:
            return
        gui.invokeMarker(self.componentID, 'updateLootingVisible', False)
        SoundGroups.g_instance.playSound2D(VDAY_LOOT_CAPTURE_STOP_SOUND)
        WWISE.WW_setRTCPGlobal(VDAY_LOOT_CAPTURE_RTPC, 0)
        self._isStickyFromConfig = self._config.get('is_sticky', True)
        gui.setMarkerSticky(self.componentID, self._isStickyFromConfig)

    def _cancelTimer(self):
        if self._tickTimerId is not None:
            BigWorld.cancelCallback(self._tickTimerId)
            self._tickTimerId = None
        return

    def clear(self):
        self._cancelTimer()
        SoundGroups.g_instance.playSound2D(VDAY_LOOT_CAPTURE_COMPLETE_SOUND)
        WWISE.WW_setRTCPGlobal(VDAY_LOOT_CAPTURE_RTPC, 0)
        if StoryModeLootableComponent.__name__ in self._entity.components:
            self._entity.StoryModeLootableComponent.onStartCapturing -= self._onStartCapturing
            self._entity.StoryModeLootableComponent.onStopCapturing -= self._onStopCapturing
        super(LootMarkerComponent, self).clear()


class LootMinimapComponent(BaseMinimapMarkerComponent):

    @classmethod
    def configReader(cls, section):
        config = super(LootMinimapComponent, cls).configReader(section)
        config.update({'loot_type': section.readString('loot_type')})
        return config

    @property
    def maskType(self):
        return ComponentBitMask.MINIMAP_MARKER

    def _setupMarker(self, gui, **kwargs):
        super(LootMinimapComponent, self)._setupMarker(gui, **kwargs)
        gui.invoke(self.componentID, 'setLootType', self._config['loot_type'])
        gui.invoke(self._componentID, 'animate')


class AbilityMinimapComponent(BaseMinimapMarkerComponent):

    @property
    def maskType(self):
        return ComponentBitMask.MINIMAP_MARKER

    def _setupMarker(self, gui, **kwargs):
        super(AbilityMinimapComponent, self)._setupMarker(gui, **kwargs)
        gui.invoke(self._componentID, 'animate')


class AbilityReconMinimapComponent(AbilityMinimapComponent):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, config, matrixProduct, entity=None, targetID=INVALID_TARGET_ID, isVisible=True):
        super(AbilityReconMinimapComponent, self).__init__(config, matrixProduct, entity, targetID, isVisible)
        self._circlesID = None
        return

    def _createMarker(self, **kwargs):
        super(AbilityReconMinimapComponent, self)._createMarker(**kwargs)
        reconItem = self._sessionProvider.shared.equipments.getEquipmentByName(RECON_ABILITY)
        if reconItem:
            self._addRangeCircle(self.position, reconItem.getDescriptor().directVisionRadius)

    def _deleteMarker(self):
        super(AbilityReconMinimapComponent, self)._deleteMarker()
        self._removeRangeCircle()

    def _addRangeCircle(self, position, viewRangeRadius):
        gui = self._gui()
        if gui is not None and self._circlesID is None:
            matrix = Math.Matrix()
            matrix.setTranslate(position)
            minimapComponent = gui.parentObj
            self._circlesID = minimapComponent.addEntry(ENTRY_SYMBOL_NAME.VIEW_RANGE_CIRCLES, CONTAINER_NAME.PERSONAL, matrix=matrix, active=True)
            bottomLeft, upperRight = minimapComponent.getBoundingBox()
            width, height = self._applyScale(upperRight[0] - bottomLeft[0], upperRight[1] - bottomLeft[1])
            minimapComponent.invoke(self._circlesID, VIEW_RANGE_CIRCLES_AS3_DESCR.AS_INIT_ARENA_SIZE, width, height)
            minimapComponent.invoke(self._circlesID, VIEW_RANGE_CIRCLES_AS3_DESCR.AS_ADD_DYN_CIRCLE, CIRCLE_STYLE.COLOR.VIEW_RANGE, CIRCLE_STYLE.ALPHA, viewRangeRadius)
        return

    def _removeRangeCircle(self):
        gui = self._gui()
        if gui is not None and self._circlesID is not None:
            gui.parentObj.delEntry(self._circlesID)
            self._circlesID = None
        return

    def _applyScale(self, width, height):
        return (width, height)


class AbilityReconFullscreenMapComponent(AbilityReconMinimapComponent):
    MINIMAP_SIZE = (352, 352)

    @property
    def maskType(self):
        return ComponentBitMask.FULLSCREEN_MAP_MARKER

    def _applyScale(self, width, height):
        widthScale = minimap_utils.MINIMAP_SIZE[0] / self.MINIMAP_SIZE[0]
        heightScale = minimap_utils.MINIMAP_SIZE[1] / self.MINIMAP_SIZE[1]
        return (widthScale * width, heightScale * width)


class AbilityLocationMarkerComponent(World2DLocationMarkerComponent):

    @property
    def bcMarkerType(self):
        return MarkerType.NON_INTERACTIVE
