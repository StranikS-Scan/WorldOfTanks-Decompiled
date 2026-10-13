# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/markers2d/markers_components.py
from __future__ import absolute_import
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from chat_commands_consts import DefaultMarkerSubType, MarkerType
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import World2DActionMarkerComponent, World2DLocationMarkerComponent, BaseMinimapMarkerComponent, ComponentBitMask
from halloween.gui.halloween_gui_constants import SoulsCollectorMarkerStates, BATTLE_CTRL_ID
from halloween.gui.battle_control.halloween_battle_constants import VEHICLE_VIEW_STATE
from gui.battle_control import avatar_getter

def getSoulsCollectorMarkerState(isFull):
    return SoulsCollectorMarkerStates.MOVE_TO_SOULS_COLLECTOR.value if isFull else SoulsCollectorMarkerStates.NOT_ENOUGHT_SOULS.value


class SoulsCollector2DActionMarkerComponent(World2DActionMarkerComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __UNHIDE_STATES_TRIGGERS = (VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED, VEHICLE_VIEW_STATE.SWITCHING)

    def __init__(self, *args, **kwargs):
        super(SoulsCollector2DActionMarkerComponent, self).__init__(*args, **kwargs)
        self._isMarkerHidden = False

    @classmethod
    def configReader(cls, section):
        config = super(SoulsCollector2DActionMarkerComponent, cls).configReader(section)
        config.update({'shape': ''})
        return config

    @property
    def hwBattleGuiCtrl(self):
        return self.__sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.HW_BATTLE_GUI_CTRL)

    def setVisible(self, isVisible):
        super(SoulsCollector2DActionMarkerComponent, self).setVisible(isVisible and not self._isMarkerHidden)

    def _setupMarker(self, gui, **kwargs):
        super(SoulsCollector2DActionMarkerComponent, self)._setupMarker(gui)
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onSoulCollectorProgress += self._updateMarkerState
            self.hwBattleGuiCtrl.onSoulCollectorProgress += self._updateMarkerProgress
        if self._entity and 'hwSoulsCollector' in self._entity.dynamicComponents:
            soulsComponent = self._entity.hwSoulsCollector
            gui.setMarkerSubType(self.componentID, DefaultMarkerSubType.ALLY_MARKER_SUBTYPE)
            gui.invokeMarker(self.componentID, 'setProgressMax', soulsComponent.capacity)
            gui.setMarkerAlwaysSticky(self.componentID)
            gui.setMarkerSticky(self.componentID, self._config['is_sticky'])
            self._updateMarkerState(soulsComponent.collected, soulsComponent.capacity, soulsComponent.isFull, soulsComponent.isCampActivated)
            self._updateMarkerProgress(soulsComponent.collected, soulsComponent.capacity, soulsComponent.isFull, soulsComponent.isCampActivated)
        return True

    def _deleteMarker(self):
        if self.hwBattleGuiCtrl:
            self.hwBattleGuiCtrl.onSoulCollectorProgress -= self._updateMarkerState
            self.hwBattleGuiCtrl.onSoulCollectorProgress -= self._updateMarkerProgress
        gui = self._gui()
        if gui:
            gui.removeMarkerAlwaysSticky(self.componentID)
        ctrl = self.__sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        super(SoulsCollector2DActionMarkerComponent, self)._deleteMarker()
        return

    def _updateMarkerState(self, collected, capacity, isFull, isCampActivated):
        gui = self._gui()
        if gui and self._isMarkerExists:
            gui.invokeMarker(self.componentID, 'setVolotState', getSoulsCollectorMarkerState(isFull))

    def _updateMarkerProgress(self, collected, capacity, isFull, isCampActivated):
        gui = self._gui()
        if gui and self._isMarkerExists:
            gui.invokeMarker(self.componentID, 'setProgress', int(collected))

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.COLLECTOR_FULL:
            self._isMarkerHidden = value
        elif state in self.__UNHIDE_STATES_TRIGGERS:
            self._isMarkerHidden = False


class Camp2DActionMarkerComponent(World2DActionMarkerComponent):

    def _setupMarker(self, gui, **kwargs):
        super(Camp2DActionMarkerComponent, self)._setupMarker(gui)
        gui.setMarkerSubType(self.componentID, DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE)
        gui.setHasAnimation(self.componentID, True)
        gui.onReplyFeedbackReceived += self._updateSticky
        return True

    def _deleteMarker(self):
        gui = self._gui()
        if self._isMarkerExists and gui:
            gui.onReplyFeedbackReceived -= self._updateSticky
        super(Camp2DActionMarkerComponent, self)._deleteMarker()

    def _updateSticky(self, componentID, isSticky):
        if self._componentID != componentID:
            return
        gui = self._gui()
        if self._isMarkerExists and gui:
            gui.setMarkerSticky(self.componentID, isSticky)


class HWLootMarkerComponent(World2DLocationMarkerComponent):
    _guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    @property
    def bcMarkerType(self):
        return MarkerType.NON_INTERACTIVE

    @property
    def _hwLootableComponent(self):
        return self._entity.dynamicComponents.get('HWLootableComponent') if self._entity else None

    def _setupMarker(self, gui, **kwargs):
        super(HWLootMarkerComponent, self)._setupMarker(gui, **kwargs)
        gui.invokeMarker(self.componentID, 'updateLootType', None, '')
        if self._hwLootableComponent:
            self._hwLootableComponent.onCapturingEntitiesChanged += self._onCapturingEntitiesChanged
            if self._hwLootableComponent.isCapturing:
                self._togglePlayerSn()
        avatar = BigWorld.player()
        if avatar is not None:
            avatar.onAvatarVehicleChanged += self._onAvatarVehicleChanged
        return

    def _togglePlayerSn(self):
        if self._hwLootableComponent:
            self._guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.LOOT, (avatar_getter.getVehicleIDAttached() in self._hwLootableComponent.looterEntities, self._hwLootableComponent.captureTime, self._hwLootableComponent.startTime))

    def _onCapturingEntitiesChanged(self):
        self._togglePlayerSn()

    def _onAvatarVehicleChanged(self):
        self._togglePlayerSn()

    def clear(self):
        if self._hwLootableComponent:
            self._hwLootableComponent.onCapturingEntitiesChanged -= self._onCapturingEntitiesChanged
        avatar = BigWorld.player()
        if avatar is not None:
            avatar.onAvatarVehicleChanged -= self._onAvatarVehicleChanged
        super(HWLootMarkerComponent, self).clear()
        return


class HWLootMinimapComponent(BaseMinimapMarkerComponent):

    @property
    def maskType(self):
        return ComponentBitMask.MINIMAP_MARKER

    def _setupMarker(self, gui, **kwargs):
        super(HWLootMinimapComponent, self)._setupMarker(gui, **kwargs)
        gui.invoke(self.componentID, 'setLootType', None)
        gui.invoke(self._componentID, 'animate')
        return
