# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/plugins.py
import BigWorld
import Math
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES
from supply_shared import Supply
from gui.Scaleform.daapi.view.battle.shared.markers2d import markers
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import VehicleMarkerPlugin
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _EVENT_ID
_EPIC_STATUS_EFFECTS_PRIORITY = (BATTLE_MARKER_STATES.STUN_STATE,
 BATTLE_MARKER_STATES.FL_REGENERATION_KIT_STATE,
 BATTLE_MARKER_STATES.REPAIRING_STATE,
 BATTLE_MARKER_STATES.ENGINEER_STATE,
 BATTLE_MARKER_STATES.HEALING_STATE,
 BATTLE_MARKER_STATES.BERSERKER_STATE,
 BATTLE_MARKER_STATES.STEALTH_STATE,
 BATTLE_MARKER_STATES.INSPIRING_STATE,
 BATTLE_MARKER_STATES.DEBUFF_STATE,
 BATTLE_MARKER_STATES.INSPIRED_STATE,
 BATTLE_MARKER_STATES.EPIC_SUPPLY_REPAIR_SELF_STATE)
_SUPPLY_VEHICLE_SYMBOL_LINKAGE = 'SupplyVehicleMarkerUI'
_SUPPLY_AIRSHIP_SYMBOL_LINKAGE = 'SupplyAirshipVehicleMarkerUI'
_MARKER_AIRSHIP_VERTICAL_OFFSET = -25
_MARKER_AIRSHIP_DEEP_OFFSET = -10
_MARKER_MORTAR_DEEP_OFFSET = 0.7

class EpicVehicleMarker(markers.VehicleMarker):

    @classmethod
    def adjustOffset(cls, vProxy):
        supplyTag = Supply.getSupplyTag(vProxy.typeDescriptor.type)
        if supplyTag:
            if Supply.isAirShip(supplyTag):
                return Math.Vector3(0, _MARKER_AIRSHIP_VERTICAL_OFFSET, _MARKER_AIRSHIP_DEEP_OFFSET)
            if Supply.isMortar(supplyTag):
                return Math.Vector3(0, 0, _MARKER_MORTAR_DEEP_OFFSET)
        return super(EpicVehicleMarker, cls).adjustOffset(vProxy)


class EpicVehicleMarkerPlugin(VehicleMarkerPlugin):
    _DELAYABLE_MARKERS = {_EVENT_ID.DETECTED_BY_THERMAL_VISION, _EVENT_ID.FRONTLINE_SUPPLY_REPAIR_TIMER}

    def __init__(self, parentObj, clazz=EpicVehicleMarker):
        super(EpicVehicleMarkerPlugin, self).__init__(parentObj, clazz)
        self.__chatCommands = self.sessionProvider.shared.chatCommands

    def getSupplyTag(self, vehicleID):
        vInfo = self.sessionProvider.getArenaDP().getVehicleInfo(vehicleID)
        return Supply.getSupplyTag(vInfo.vehicleType)

    def _showMarkerCondition(self, focusedMarker, vehicleID):
        supplyTag = self.getSupplyTag(vehicleID)
        if not supplyTag:
            return super(EpicVehicleMarkerPlugin, self)._showMarkerCondition(focusedMarker, vehicleID)
        elif focusedMarker.getIsPlayerTeam() and not focusedMarker.isAlive():
            vehicle = BigWorld.entities.get(vehicleID)
            resurrectComp = vehicle.dynamicComponents.get('supplyResurrectComponent', None)
            return resurrectComp is not None
        else:
            return super(EpicVehicleMarkerPlugin, self)._showMarkerCondition(focusedMarker, vehicleID)

    def _getMarkerStatusPriority(self, markerState):
        try:
            return _EPIC_STATUS_EFFECTS_PRIORITY.index(markerState.statusID)
        except ValueError:
            return -1

    def _onVehicleMarkerAdded(self, vProxy, vInfo, guiProps):
        super(EpicVehicleMarkerPlugin, self)._onVehicleMarkerAdded(vProxy, vInfo, guiProps)
        supplyTag = self.getSupplyTag(vInfo.vehicleID)
        if supplyTag and Supply.isAirShip(supplyTag) and vInfo.isEnemy():
            self.__chatCommands.handleChatCommand(BATTLE_CHAT_COMMAND_NAMES.FOCUS_SUPPLY, targetID=vInfo.vehicleID)

    def _getMarkerSymbol(self, vehicleID):
        supplyTag = self.getSupplyTag(vehicleID)
        if supplyTag:
            if Supply.isAirShip({supplyTag}):
                return _SUPPLY_AIRSHIP_SYMBOL_LINKAGE
            return _SUPPLY_VEHICLE_SYMBOL_LINKAGE
        return super(EpicVehicleMarkerPlugin, self)._getMarkerSymbol(vehicleID)

    def _setMarkerInitialState(self, marker, vInfo):
        super(EpicVehicleMarkerPlugin, self)._setMarkerInitialState(marker, vInfo)
        if Supply.isSupply(vInfo.vehicleType.tags):
            self.__setSupplyInfo(marker, vInfo)

    def _hideVehicleMarker(self, vehicleID):
        self._destroyVehicleMarker(vehicleID)

    def _processRegularMarker(self, eventID, vehicleID, value):
        super(EpicVehicleMarkerPlugin, self)._processRegularMarker(eventID, vehicleID, value)
        marker = self._markers[vehicleID]
        handle = marker.getMarkerID()
        if eventID == _EVENT_ID.VEHICLE_FRONTLINE_STEALTH_RADAR_ACTIVE:
            self.__updateStealthRadarMarker(vehicleID, handle, value)
        elif eventID == _EVENT_ID.VEHICLE_FRONTLINE_REGENERATION_KIT_ACTIVE:
            self.__updateFLRegenerationKitMarker(vehicleID, handle, value)
        elif eventID == _EVENT_ID.FRONTLINE_SUPPLY_REPAIR_TIMER:
            self.__updateFLSupplyRepairTimer(vehicleID, handle, value)

    def __updateStealthRadarMarker(self, vehicleID, handle, info):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is None or not vehicle.isAlive() or info is None:
            return
        else:
            duration = info.duration if info.isActive else 0
            self._updateMarkerTimer(vehicleID, handle, duration, BATTLE_MARKER_STATES.STEALTH_STATE, True)
            return

    def __updateFLRegenerationKitMarker(self, vehicleID, handle, info):
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is None or not vehicle.isAlive():
            return
        else:
            duration = info.duration if info.isActive else 0
            self._updateMarkerTimer(vehicleID, handle, duration, BATTLE_MARKER_STATES.FL_REGENERATION_KIT_STATE, True)
            return

    def __updateFLSupplyRepairTimer(self, vehicleID, handle, duration):
        self._updateMarkerTimer(vehicleID, handle, duration, BATTLE_MARKER_STATES.EPIC_SUPPLY_REPAIR_SELF_STATE)

    def __setSupplyInfo(self, marker, vInfo):
        self._invokeMarker(marker.getMarkerID(), 'setSupplyType', Supply.getSupplyTag(vInfo.vehicleType))


class EpicRespawnableVehicleMarkerPlugin(EpicVehicleMarkerPlugin):

    def start(self):
        super(EpicRespawnableVehicleMarkerPlugin, self).start()
        self._isSquadIndicatorEnabled = False
