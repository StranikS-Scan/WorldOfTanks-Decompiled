# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/markers2d.py
import logging
from itertools import chain
from functools import partial
from helpers import i18n
import BigWorld
import Math
from helpers.CallbackDelayer import CallbackDelayer
from HBVehicleRoleComponent import HBVehicleRoleComponent
from account_helpers.settings_core.settings_constants import MARKERS
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_control import avatar_getter
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import SettingsPlugin, MarkerPlugin, TeamsOrControlsPointsPlugin, BaseAreaMarkerPlugin, settings, _EQUIPMENT_DELAY_FORMAT, _EQUIPMENT_DEFAULT_INTERVAL
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.markers import ReplyStateForMarker, VehicleMarker
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from chat_commands_consts import MarkerType, INVALID_TARGET_ID, LocationMarkerSubType
from battleground.location_point_manager import g_locationPointManager
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from historical_battles_common.hb_constants import VehicleRole
from historical_battles.gui.Scaleform.daapi.view.battle.markers import HBObjectivesMarker
from historical_battles.gui.Scaleform.daapi.view.battle.components import HBStaticObjectivesMarkerComponent, HBVehicleObjectivesMarkerComponent, HBChatCommunicationComponent, cancelPlayerReplyForMarker
from TeamBase import CAPTURE_POINTS_LIMIT
_logger = logging.getLogger('markers2d')
_MARKERS_SYMBOL = 'HBVehicleMarker'
_HISTORICAL_BATTLE_BASE_ID = 8
_MARKER_ALLY_BOT = 'allyBot'
_MARKERS_ALL = MARKERS.ALL() + (_MARKER_ALLY_BOT,)
_FLAG_COLOR_ALLY = Math.Vector4(97, 191, 34, 255)
_FLAG_COLOR_ENEMY = Math.Vector4(200, 20, 0, 255)

class HBVehicleMarkerSettingsPlugin(SettingsPlugin):
    __SETTINGS = {None: (('markerBaseIcon', False),
            ('markerBaseLevel', False),
            ('markerBaseHpIndicator', True),
            ('markerBaseDamage', True),
            ('markerBaseVehicleName', True),
            ('markerBaseAimMarker2D', True),
            ('markerAltIcon', False),
            ('markerAltLevel', False),
            ('markerAltHpIndicator', True),
            ('markerAltDamage', True),
            ('markerAltVehicleName', True),
            ('markerAltAimMarker2D', True)),
     MARKERS.ALLY: (('markerBasePlayerName', True), ('markerAltPlayerName', True)),
     _MARKER_ALLY_BOT: (('markerBasePlayerName', False), ('markerAltPlayerName', False)),
     MARKERS.ENEMY: (('markerBasePlayerName', False), ('markerAltPlayerName', False)),
     MARKERS.DEAD: (('markerBasePlayerName', False),
                    ('markerAltPlayerName', False),
                    ('markerAltLevel', False),
                    ('markerAltHpIndicator', False),
                    ('markerBaseAimMarker2D', False),
                    ('markerBaseHpIndicator', False),
                    ('markerBaseDamage', False),
                    ('markerBaseVehicleName', False),
                    ('markerAltDamage', False),
                    ('markerAltVehicleName', False),
                    ('markerAltAimMarker2D', False),
                    ('markerAltHp', 3),
                    ('markerBaseHp', 3))}

    def _setMarkerSettings(self, notify=False):
        getter = self.settingsCore.getSetting
        result = {}
        for name in _MARKERS_ALL:
            settingsCoreName = MARKERS.ALLY if name == _MARKER_ALLY_BOT else name
            stgs = getter(settingsCoreName)
            for custOptName, custOptVal in chain(self.__SETTINGS[None], self.__SETTINGS[name]):
                if custOptName not in stgs:
                    _logger.warning('Option "%s" is not in list of options. Skipped.', custOptName)
                    continue
                stgs[custOptName] = custOptVal

            result[name] = stgs

        self._parentObj.setMarkerSettings(result, notify=notify)
        return


class HBVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin, HBStaticObjectivesMarkerComponent, HBVehicleObjectivesMarkerComponent):
    CHECK_DISTANCE_CALLBACK_TIME = 1.0

    def __init__(self, parentObj, clazz=VehicleMarker):
        super(HBVehicleMarkerPlugin, self).__init__(parentObj, clazz)
        self.__objectives = dict()
        self.__distanceCallback = CallbackDelayer()

    def start(self):
        super(HBVehicleMarkerPlugin, self).start()
        HBVehicleRoleComponent.onRoleUpdated += self._onVehicleRoleUpdated
        HBStaticObjectivesMarkerComponent.start(self)
        HBVehicleObjectivesMarkerComponent.start(self)

    def stop(self):
        self.__distanceCallback.destroy()
        self.__objectives.clear()
        HBVehicleObjectivesMarkerComponent.stop(self)
        HBStaticObjectivesMarkerComponent.stop(self)
        HBVehicleRoleComponent.onRoleUpdated -= self._onVehicleRoleUpdated
        super(HBVehicleMarkerPlugin, self).stop()

    def _setMarkerInitialState(self, marker, vInfo):
        super(HBVehicleMarkerPlugin, self)._setMarkerInitialState(marker, vInfo)
        vehicleID = marker.getVehicleID()
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle is None:
            return
        else:
            if 'roleComponent' in vehicle.dynamicComponents:
                self.__updateVehicleRole(marker, vehicle.roleComponent)
            targetID = self._getTargetIDFromVehicleID(vehicleID)
            if targetID in self.__objectives:
                self._setupObjectivesMarker(self.__objectives[targetID])
            arenaDP = self.sessionProvider.getArenaDP()
            vInfo = arenaDP.getVehicleInfo(vehicleID)
            self._invokeMarker(marker.getMarkerID(), 'setIsBot', vInfo.isBot)
            if arenaDP.isAlly(vehicleID) and vInfo.vehicleType.classTag == VEHICLE_CLASS_NAME.SPG:
                self._invokeMarker(marker.getMarkerID(), 'showShield')
            return

    def _onVehicleRoleUpdated(self, component):
        marker = self._markers.get(component.entity.id)
        if marker:
            self.__updateVehicleRole(marker, component)

    def _getMarkerSymbol(self, vehicleID):
        return _MARKERS_SYMBOL

    def __updateVehicleRole(self, marker, component):
        roleIcon = None
        if component.vehicleRole != VehicleRole.regular:
            roleIcon = component.getRoleIconName()
        self._invokeMarker(marker.getMarkerID(), 'overrideTypeIcon', roleIcon)
        return

    def _getMarker(self, markerID, markerType, defaultMarker=None):
        if markerType == MarkerType.LOCATION_MARKER_TYPE:
            return self.__objectives.get(markerID, defaultMarker)
        return self._markers.get(markerID, defaultMarker) if markerType == self.getMarkerType() else defaultMarker

    def _getTargetIDFromVehicleID(self, vehicleID):
        return next((tID for tID, marker in self.__objectives.iteritems() if marker.ownVehicleID == vehicleID), INVALID_TARGET_ID)

    def _getMarkerFromTargetID(self, targetID, markerType):
        return self._getMarker(targetID, markerType)

    def _addMarker(self, targetID, position, featureID):
        if featureID and position is not None:
            if self.sessionProvider.getArenaDP().isAlly(featureID):
                return
            marker = HBObjectivesMarker(targetID, position, True, LocationMarkerSubType.OBJECTIVES_POINT_SUBTYPE)
            if featureID:
                marker.ownVehicleID = featureID
                marker.isAlly = self.sessionProvider.getArenaDP().isAlly(featureID)
            marker.isGoalForPlayer = False
            self.__objectives[targetID] = marker
            if featureID in self._markers:
                self._setupObjectivesMarker(marker)
        return

    def _removeMarker(self, targetID, markerType):
        objectives = self._getMarkerFromTargetID(targetID, markerType)
        if objectives is not None:
            vehicleID = objectives.ownVehicleID
            marker = self._getMarkerFromTargetID(vehicleID, self.getMarkerType())
            if marker is not None:
                super(HBVehicleMarkerPlugin, self)._setMarkerSticky(marker.getMarkerID(), False)
                if self.__distanceCallback.hasDelayedCallback(self.__checkDistanceForPlayerCB):
                    self.__distanceCallback.stopCallback(self.__checkDistanceForPlayerCB)
                self._invokeMarker(marker.getMarkerID(), 'initBossMarker', -1, '')
            del self.__objectives[targetID]
        return

    def _setupObjectivesMarker(self, marker):
        playerVehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        if playerVehicle is None:
            return
        else:
            vehicleID = marker.ownVehicleID
            markerID = self._markers[vehicleID].getMarkerID()
            self._setVehicleMatrixAndLocation(marker, vehicleID)
            distance = (marker.getPosition() - playerVehicle.position).length
            if distance is not None:
                self._setMarkerTextLabelEnabled(markerID, False)
                self._invokeMarker(markerID, 'initBossMarker', distance, backport.text(R.strings.hb_battle.inbattle_markers.distance_str()))
                if not self.sessionProvider.getCtx().isPlayerObserver() and avatar_getter.isVehicleAlive():
                    super(HBVehicleMarkerPlugin, self)._setMarkerSticky(markerID, True)
                if not self.__distanceCallback.hasDelayedCallback(self.__checkDistanceForPlayerCB):
                    self.__distanceCallback.delayCallback(self.CHECK_DISTANCE_CALLBACK_TIME, self.__checkDistanceForPlayerCB)
            return

    def _setMarkerSticky(self, markerID, isSticky):
        vehicleID = self.getTargetIDFromMarkerID(markerID)
        if vehicleID == INVALID_TARGET_ID:
            return
        else:
            vehicle = BigWorld.entities.get(vehicleID)
            if vehicle is not None and vehicle.isAlive():
                objectiveID = self._getTargetIDFromVehicleID(vehicleID)
                if objectiveID != INVALID_TARGET_ID:
                    return
            super(HBVehicleMarkerPlugin, self)._setMarkerSticky(markerID, isSticky)
            return

    def __checkDistanceForPlayerCB(self):
        playerVehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        if playerVehicle is None and self.__objectives:
            return
        else:
            for marker in self.__objectives.itervalues():
                distance = (marker.getPosition() - playerVehicle.position).length
                vehMarker = self._getMarkerFromTargetID(marker.ownVehicleID, self.getMarkerType())
                if vehMarker is not None and distance is not None:
                    self._invokeMarker(vehMarker.getMarkerID(), 'setHBDistance', distance)

            return self.CHECK_DISTANCE_CALLBACK_TIME

    def _updateMarker(self, targetID, isReplied, replierVehicleID):
        pass


class HBObjectivesMarkerPlugin(MarkerPlugin, HBStaticObjectivesMarkerComponent, HBVehicleObjectivesMarkerComponent, HBChatCommunicationComponent):
    __slots__ = ('_clazz', '_markers', '__distanceCallback')
    CHECK_DISTANCE_CALLBACK_TIME = 1.5

    def __init__(self, parentObj, clazz=HBObjectivesMarker):
        super(HBObjectivesMarkerPlugin, self).__init__(parentObj)
        self._clazz = clazz
        self._markers = dict()
        self.__distanceCallback = CallbackDelayer()

    def start(self):
        HBStaticObjectivesMarkerComponent.start(self)
        HBVehicleObjectivesMarkerComponent.start(self)
        HBChatCommunicationComponent.start(self)

    def stop(self):
        self.__distanceCallback.destroy()
        self._clearMarkers()
        HBChatCommunicationComponent.stop(self)
        HBStaticObjectivesMarkerComponent.stop(self)
        HBVehicleObjectivesMarkerComponent.stop(self)

    def getMarkerType(self):
        return MarkerType.LOCATION_MARKER_TYPE

    def getMarkerSubType(self):
        return LocationMarkerSubType.OBJECTIVES_POINT_SUBTYPE

    def getTargetIDFromMarkerID(self, markerID):
        return next((tID for tID, marker in self._markers.iteritems() if marker.getMarkerID() == markerID), INVALID_TARGET_ID)

    def _getTargetIDFromVehicleID(self, vehicleID):
        return next((tID for tID, marker in self._markers.iteritems() if marker.ownVehicleID == vehicleID), INVALID_TARGET_ID)

    def _getMarker(self, markerID, markerType, defaultMarker=None):
        return self._markers.get(markerID, defaultMarker) if markerType == self.getMarkerType() else defaultMarker

    def _getMarkerFromTargetID(self, targetID, markerType):
        return self._getMarker(targetID, markerType)

    def _getMarkerText(self):
        return backport.text(R.strings.hb_battle.inbattle_markers.going_there())

    def _addMarker(self, targetID, position, featureID):
        if featureID and self.sessionProvider.getArenaDP().isAlly(featureID):
            return
        markerID = self._createMarkerWithPosition(self._clazz.FLASH_SYMBOL_NAME, position)
        self._setMarkerRenderInfo(markerID, self._clazz.STATIC_MARKER_MIN_SCALE, self._clazz.STATIC_MARKER_BOUNDS, self._clazz.INNER_STATIC_MARKER_BOUNDS, self._clazz.STATIC_MARKER_CULL_DISTANCE, self._clazz.STATIC_MARKER_BOUNDS_MIN_SCALE)
        self._setMarkerLocationOffset(markerID, self._clazz.MIN_Y_OFFSET, self._clazz.MAX_Y_OFFSET, self._clazz.DISTANCE_FOR_MIN_Y_OFFSET, self._clazz.MAX_Y_BOOST, self._clazz.BOOST_START)
        marker = self._clazz(markerID, position, False, self.getMarkerSubType())
        if featureID:
            marker.ownVehicleID = featureID
        marker.setState(ReplyStateForMarker.NO_ACTION)
        self._markers[targetID] = marker
        self._setActiveState(marker, ReplyStateForMarker.NO_ACTION)
        self._setVehicleMatrixAndLocation(marker, featureID)
        if self.sessionProvider.getCtx().isPlayerObserver() or not avatar_getter.isVehicleAlive():
            self._setMarkerBoundEnabled(marker.getMarkerID(), False)
        else:
            self._setMarkerBoundEnabled(marker.getMarkerID(), True)
            super(HBObjectivesMarkerPlugin, self)._setMarkerSticky(markerID, True)
            if not self.__distanceCallback.hasDelayedCallback(self.__checkDistanceForPlayerCB):
                self.__distanceCallback.delayCallback(self.CHECK_DISTANCE_CALLBACK_TIME, self.__checkDistanceForPlayerCB)

    def _removeMarker(self, targetID, markerType):
        marker = self._getMarkerFromTargetID(targetID, markerType)
        if marker is not None:
            self._destroyMarker(marker.getMarkerID())
            del self._markers[targetID]
        return

    def _clearMarkers(self):
        for marker in self._markers.itervalues():
            self._destroyMarker(marker.getMarkerID())

        self._markers.clear()

    def _setMarkerSticky(self, markerID, isSticky):
        targetID = self.getTargetIDFromMarkerID(markerID)
        if targetID == INVALID_TARGET_ID:
            return
        else:
            advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
            if advChatCmp is not None:
                chatCmdData = advChatCmp.getCommandDataForTargetIDAndMarkerType(targetID, self.getMarkerType())
                if chatCmdData is not None:
                    if chatCmdData.commandCreatorVehID != self.sessionProvider.arenaVisitor.getArenaUniqueID():
                        super(HBObjectivesMarkerPlugin, self)._setMarkerSticky(markerID, isSticky)
            return

    def __checkDistanceForPlayerCB(self):
        playerVehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        if playerVehicle is None:
            return
        else:
            for targetID, marker in self._markers.iteritems():
                distance = (marker.getPosition() - playerVehicle.position).length
                isSoClose = distance < marker.DISTANCE_FOR_MARKER_HIDE
                if marker.ownVehicleID:
                    marker.isInAOI = self.__checkTargetIsInAOI(marker.ownVehicleID)
                    if g_locationPointManager is not None:
                        location = g_locationPointManager.markedAreas.get(targetID)
                        if location is not None:
                            location.position = marker.getPosition()
                self._setMarkerActive(marker.getMarkerID(), not (isSoClose or marker.isInAOI))
                if marker.setActive(not isSoClose) and isSoClose:
                    cancelPlayerReplyForMarker(self.sessionProvider, targetID, self.getMarkerType())

            return self.CHECK_DISTANCE_CALLBACK_TIME

    def __checkTargetIsInAOI(self, vehicleID):
        vehicle = BigWorld.entities.get(vehicleID)
        return vehicle is not None and vehicle.isStarted

    def _updateMarker(self, targetID, isReplied, replierVehicleID):
        pass


class HBTeamsOrControlsPointsPlugin(TeamsOrControlsPointsPlugin):

    def start(self):
        super(HBTeamsOrControlsPointsPlugin, self).start()
        ctrl = self.sessionProvider.dynamic.teamBases
        if ctrl is not None:
            ctrl.onBaseTeamChanged += self.__onBaseTeamChanged
            ctrl.onTeamBasePointsUpdated += self.__onTeamBasePointsUpdated
            ctrl.onBaseCapturingStopped += self.__onBaseCapturingStopped
        return

    def stop(self):
        super(HBTeamsOrControlsPointsPlugin, self).stop()
        ctrl = self.sessionProvider.dynamic.teamBases
        if ctrl is not None:
            ctrl.onBaseTeamChanged -= self.__onBaseTeamChanged
            ctrl.onTeamBasePointsUpdated -= self.__onTeamBasePointsUpdated
            ctrl.onBaseCapturingStopped -= self.__onBaseCapturingStopped
        return

    def _getMarkerIdentifier(self):
        return _HISTORICAL_BATTLE_BASE_ID

    def _addTeamBasePositions(self):
        teamBases = self.sessionProvider.dynamic.teamBases.getTeamBases()
        for base in teamBases.itervalues():
            if base.team == self._personalTeam:
                owner = 'ally'
            else:
                owner = 'enemy'
            markerID = self._addBaseOrControlPointMarker(owner, base.position, base.baseID)
            if markerID is not None:
                self._invokeMarker(markerID, 'setIsEpicMarker', True)

        return

    def __onBaseTeamChanged(self, baseID, team):
        marker = self._markers.get(baseID)
        isPlayerTeam = team == self._personalTeam
        if marker is not None:
            owner = 'ally' if isPlayerTeam else 'enemy'
            self._invokeMarker(marker.getMarkerID(), 'setCapturePoints', 0)
            self._invokeMarker(marker.getMarkerID(), 'setOwningTeam', owner)
            self._setActiveState(marker, marker.getState())
        flagColor = _FLAG_COLOR_ALLY if isPlayerTeam else _FLAG_COLOR_ENEMY
        BigWorld.wg_setBaseFlagColor(baseID, flagColor / 255)
        return

    def _isMarkerSticky(self):
        return True

    def __onTeamBasePointsUpdated(self, baseID, points):
        marker = self._markers.get(baseID)
        if marker is not None:
            self._invokeMarker(marker.getMarkerID(), 'setCapturePoints', points / CAPTURE_POINTS_LIMIT)
        return

    def __onBaseCapturingStopped(self, baseID, team):
        marker = self._markers.get(baseID)
        if marker is not None:
            self._invokeMarker(marker.getMarkerID(), 'setCapturePoints', 0)
        return


class HBAreaMarkerPlugin(BaseAreaMarkerPlugin):

    def _getUnitText(self):
        return backport.text(R.strings.hb_battle.inbattle_markers.distance_str())


class HBEquipmentsMarkerPlugin(MarkerPlugin):
    __slots__ = ('__callbackIDs', '__defaultPostfix')

    def __init__(self, parentObj):
        super(HBEquipmentsMarkerPlugin, self).__init__(parentObj)
        self.__callbackIDs = {}
        self.__defaultPostfix = i18n.makeString(INGAME_GUI.FORTCONSUMABLES_TIMER_POSTFIX)

    def start(self):
        super(HBEquipmentsMarkerPlugin, self).init()
        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentMarkerShown += self.__onEquipmentMarkerShown
        return

    def stop(self):
        while self.__callbackIDs:
            _, callbackID = self.__callbackIDs.popitem()
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        ctrl = self.sessionProvider.shared.equipments
        if ctrl is not None:
            ctrl.onEquipmentMarkerShown -= self.__onEquipmentMarkerShown
        super(HBEquipmentsMarkerPlugin, self).stop()
        return

    def __onEquipmentMarkerShown(self, item, position, *_):
        markerID = self._createMarkerWithPosition(settings.MARKER_SYMBOL_NAME.EQUIPMENT_MARKER, position + settings.MARKER_POSITION_ADJUSTMENT)
        markerName = item.getMarker()
        markerColor = item.getMarkerColor()
        delay = item.getDelay()
        duration = item.getDuration()
        self._invokeMarker(markerID, 'init', markerName, _EQUIPMENT_DELAY_FORMAT.format(round(delay)), self.__defaultPostfix, markerColor)
        delayFinishTime = BigWorld.serverTime() + delay
        totalFinishTime = delayFinishTime + duration
        self.__setCallback(markerID, delayFinishTime, totalFinishTime, markerName, markerColor)

    def __setCallback(self, markerID, delayFinishTime, totalFinishTime, markerName, markerColor, hideText=True, interval=_EQUIPMENT_DEFAULT_INTERVAL):
        self.__callbackIDs[markerID] = BigWorld.callback(interval, partial(self.__handleCallback, markerID, delayFinishTime, totalFinishTime, markerName, markerColor, hideText))

    def __clearCallback(self, markerID):
        callbackID = self.__callbackIDs.pop(markerID, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        return

    def __handleCallback(self, markerID, delayFinishTime, totalFinishTime, markerName, markerColor, hideText):
        self.__callbackIDs[markerID] = None
        remainingDelay = delayFinishTime - BigWorld.serverTime()
        remainingTotalTime = totalFinishTime - BigWorld.serverTime()
        if remainingTotalTime > 0:
            if remainingDelay > 0:
                self._invokeMarker(markerID, 'updateTimer', _EQUIPMENT_DELAY_FORMAT.format(abs(round(remainingDelay))))
            elif hideText:
                self._invokeMarker(markerID, 'init', markerName, '', '', markerColor)
                hideText = False
            self.__setCallback(markerID, delayFinishTime, totalFinishTime, markerName, markerColor, hideText, min(remainingDelay, _EQUIPMENT_DEFAULT_INTERVAL))
        else:
            self._destroyMarker(markerID)
        return
