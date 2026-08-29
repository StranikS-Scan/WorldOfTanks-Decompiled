# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/plugins.py
import math
import BigWorld
from shared_utils import safeCancelCallback
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import EventBusPlugin, AreaMarkerPlugin, ChatCommunicationComponent
from gui.Scaleform.daapi.view.battle.shared.markers2d.vehicle_plugins import RespawnableVehicleMarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d.markers import BaseMarker, ReplyStateForMarker
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.arena_vos import VehicleActions, EventKeys
from gui.battle_control.battle_constants import PLAYER_GUI_PROPS
from chat_commands_consts import INVALID_MARKER_SUBTYPE, INVALID_MARKER_ID, MarkerType, DefaultMarkerSubType
from gui.impl import backport
from gui.impl.gen import R
from gui.wt_event.wt_event_helpers import isBossTeam
from helpers.time_utils import ONE_SECOND
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_BATTLE_MARKER_STATES import WHITE_TIGER_BATTLE_MARKER_STATES
from white_tiger.gui.gui_constants import FEEDBACK_EVENT_ID
from wt_settings import g_wt_config
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from WTTeamInfoComponent import WTCloneInfoEvent

class WhiteTigerVehicleMarkerPlugin(RespawnableVehicleMarkerPlugin):
    WT_VEHICLE_MARKER = 'WTVehicleMarkerUI'
    WT_GENERATOR_MARKER = 'GeneratorLocationMarkerUI'
    WT_DOME_MARKER = 'StaticShieldMarkerUI'

    def __init__(self, parentObj):
        super(WhiteTigerVehicleMarkerPlugin, self).__init__(parentObj)
        self.__cloneVehicleIDs = set()
        self.__cloneLifeTimes = {}
        self.__cloneRemainingTimes = {}
        self.__cloneSpawnTimes = {}
        self.__cloneTimerCallbackID = None
        self.__allCloneVehicleIDs = set()
        return

    def start(self):
        super(WhiteTigerVehicleMarkerPlugin, self).start()
        g_eventBus.addListener(WTCloneInfoEvent.CLONE_VEHICLE_INFOS_UPDATED, self.__onCloneVehicleIDsUpdated, scope=EVENT_BUS_SCOPE.BATTLE)

    def stop(self):
        g_eventBus.removeListener(WTCloneInfoEvent.CLONE_VEHICLE_INFOS_UPDATED, self.__onCloneVehicleIDsUpdated, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__cloneVehicleIDs = set()
        self.__allCloneVehicleIDs = set()
        self.__cloneLifeTimes.clear()
        self.__cloneSpawnTimes.clear()
        self.__stopCloneTimer()
        super(WhiteTigerVehicleMarkerPlugin, self).stop()

    def _getMarkerSymbol(self, vehicleID):
        return WhiteTigerVehicleMarkerPlugin.WT_VEHICLE_MARKER

    def _onVehicleFeedbackReceived(self, eventID, vehicleID, value):
        super(WhiteTigerVehicleMarkerPlugin, self)._onVehicleFeedbackReceived(eventID, vehicleID, value)
        if vehicleID not in self._markers:
            return
        markerID = self._markers[vehicleID].getMarkerID()
        if eventID == FEEDBACK_EVENT_ID.VEHICLE_SHOW_MESSAGE:
            self._showActionMessage(markerID, *value)
        elif eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD:
            self._invokeMarker(markerID, 'setPlasmaBuffValue', 0)
            self.__dropCloneTimer(vehicleID)
        elif eventID == FEEDBACK_EVENT_ID.VEHICLE_DISCRETE_DAMAGE_RECEIVED:
            _, plasmaDamage = value
            arenaDP = self.sessionProvider.getArenaDP()
            isAlly = arenaDP.isAlly(vehicleID)
            if plasmaDamage > 0 and not isAlly:
                self._invokeMarker(markerID, 'showPlasmaDamage', plasmaDamage)
        elif eventID == FEEDBACK_EVENT_ID.WT_VEHICLE_UNION_STRENGTH_MARK:
            handle = self._markers[vehicleID].getMarkerID()
            isShown = value['isShown']
            numberOfMarks = value.get('numberOfMarks', 0) if isShown else 0
            self._updateStatusMarkerState(vehicleID, isShown, handle, WHITE_TIGER_BATTLE_MARKER_STATES.WT_UNION_STRENGTH_STATE, numberOfMarks, True, False)
        elif eventID == FEEDBACK_EVENT_ID.WT_VEHICLE_STUN_AREA_DEBUFF:
            handle = self._markers[vehicleID].getMarkerID()
            isShown = value['isShown']
            duration = value.get('duration', 0) if isShown else 0
            self._updateMarkerTimer(vehicleID, handle, duration, WHITE_TIGER_BATTLE_MARKER_STATES.WT_STUN_AREA_STATE, True, True)
        elif eventID == FEEDBACK_EVENT_ID.WT_VEHICLE_STUN_AREA_MOD_A_DEBUFF:
            handle = self._markers[vehicleID].getMarkerID()
            isShown = value['isShown']
            duration = value.get('duration', 0) if isShown else 0
            self._updateMarkerTimer(vehicleID, handle, duration, WHITE_TIGER_BATTLE_MARKER_STATES.WT_STUN_AREA_MOD_A_STATE, True, True)
        elif eventID == FEEDBACK_EVENT_ID.WT_VEHICLE_SILENCE:
            handle = self._markers[vehicleID].getMarkerID()
            isShown = value['isShown']
            duration = value.get('duration', 0) if isShown else 0
            self._updateMarkerTimer(vehicleID, handle, duration, WHITE_TIGER_BATTLE_MARKER_STATES.WT_SILENCE_STATE, True, True)
        elif eventID == FEEDBACK_EVENT_ID.WT_EXTRACTOR_SHOT_DEBUFF:
            handle = self._markers[vehicleID].getMarkerID()
            isShown = value['isShown']
            duration = value.get('duration', 0) if isShown else 0
            self._updateMarkerTimer(vehicleID, handle, duration, BATTLE_MARKER_STATES.STUN_STATE, True, True)
        elif eventID == FEEDBACK_EVENT_ID.WT_INVISIBILITY_MARK:
            handle = self._markers[vehicleID].getMarkerID()
            isShown = value['isShown']
            self._updateStatusMarkerState(vehicleID, isShown, handle, WHITE_TIGER_BATTLE_MARKER_STATES.WT_INVISIBLE_STATE, 0, True, False)

    def _showActionMessage(self, markerID, message, isAlly):
        self._invokeMarker(markerID, 'showActionMessage', message, isAlly)

    def _setVehicleInfo(self, marker, vInfo, guiProps, nameParts):
        markerID = marker.getMarkerID()
        vType = vInfo.vehicleType
        vehId = vInfo.vehicleID
        if avatar_getter.isVehiclesColorized():
            guiPropsName = 'team{}'.format(vInfo.team)
        else:
            if avatar_getter.isObserver():
                arenaDP = self.sessionProvider.getArenaDP()
                obsVehId = BigWorld.player().observedVehicleID
                if vehId == obsVehId or arenaDP.isSquadMan(vehId, arenaDP.getVehicleInfo(obsVehId).prebattleID):
                    guiProps = PLAYER_GUI_PROPS.squadman
            guiPropsName = guiProps.name()
        if self._isSquadIndicatorEnabled and vInfo.squadIndex:
            squadIndex = vInfo.squadIndex
        else:
            squadIndex = 0
        hunting = VehicleActions.isHunting(vInfo.events)
        classTag = vType.classTag
        vehCD = vType.compactDescr
        if g_wt_config.isAnyTypeBoss(vehCD):
            classTag = 'boss'
        playerFullName = nameParts.playerFullName
        playerName = nameParts.playerName
        clanAbbrev = nameParts.clanAbbrev
        regionCode = nameParts.regionCode
        if self.__isCloneVehicle(vehId):
            classTag = 'clone'
            cloneName = backport.text(R.strings.ingame_gui.wt_clone.clonePlayerName())
            playerFullName = cloneName
            playerName = cloneName
            clanAbbrev = ''
            regionCode = ''
            lifeTime = self.__cloneLifeTimes.get(vehId, 0)
            self.__setCloneRemainingTime(vehId, lifeTime)
        canShowPlasma = not isBossTeam(vInfo.team) or self.__isBossWithPlasma(vInfo)
        self._invokeMarker(markerID, 'showPlasmaBuff', canShowPlasma)
        if canShowPlasma:
            plasmaBuffValue = vInfo.gameModeSpecific.getValue(EventKeys.PLASMA_COUNT.value)
            if plasmaBuffValue is not None:
                self._invokeMarker(markerID, 'setPlasmaBuffValue', plasmaBuffValue)
        self._invokeMarker(markerID, 'setVehicleInfo', classTag, vType.iconPath, nameParts.vehicleName, vType.level, playerFullName, playerName, clanAbbrev, regionCode, vType.maxHealth, guiPropsName, hunting, squadIndex, backport.text(R.strings.ingame_gui.stun.seconds()))
        self._invokeMarker(markerID, 'update')
        return

    def __isCloneVehicle(self, vehicleID):
        return vehicleID in self.__cloneVehicleIDs

    def _needsMarker(self, vInfo):
        return False if vInfo.vehicleID in self.__allCloneVehicleIDs and not vInfo.isAlive() else super(WhiteTigerVehicleMarkerPlugin, self)._needsMarker(vInfo)

    def __onCloneVehicleIDsUpdated(self, data):
        teamInfo = BigWorld.player().arena.teamInfo
        wtCloneInfo = getattr(teamInfo, 'wtTeamInfoComponent', None)
        if wtCloneInfo is None:
            return
        else:
            self.__allCloneVehicleIDs.update(self.__cloneVehicleIDs)
            prevIDs = self.__cloneVehicleIDs
            newIDs = set()
            for vehInfo in wtCloneInfo.cloneVehicleInfos:
                vid = vehInfo['vehicleId']
                newIDs.add(vid)
                self.__cloneSpawnTimes[vid] = vehInfo['cloneSpawnTime']
                self.__cloneLifeTimes[vid] = vehInfo['cloneLifeTime']

            self.__cloneVehicleIDs = newIDs
            arenaDP = self.sessionProvider.getArenaDP()
            getParts = self.sessionProvider.getCtx().getPlayerFullNameParts
            getProps = arenaDP.getPlayerGuiProps
            for vehicleID in newIDs:
                if vehicleID not in self._markers:
                    continue
                vInfo = arenaDP.getVehicleInfo(vehicleID)
                marker = self._markers[vehicleID]
                self._setVehicleInfo(marker, vInfo, getProps(vehicleID, vInfo.team), getParts(vehicleID))

            for removedID in prevIDs.difference(newIDs):
                self.__dropCloneTimer(removedID)
                self._hideVehicleMarker(removedID)

            self.__ensureCloneTimer()
            return

    def __ensureCloneTimer(self):
        if not self.__cloneSpawnTimes:
            self.__stopCloneTimer()
            return
        else:
            if self.__cloneTimerCallbackID is None:
                self.__cloneTimerCallbackID = BigWorld.callback(ONE_SECOND, self.__onCloneTimerTick)
            return

    def __stopCloneTimer(self):
        if self.__cloneTimerCallbackID is not None:
            safeCancelCallback(self.__cloneTimerCallbackID)
            self.__cloneTimerCallbackID = None
        return

    def __onCloneTimerTick(self):
        self.__cloneTimerCallbackID = None
        if not self.__cloneSpawnTimes:
            return
        else:
            now = BigWorld.serverTime()
            expiredTimers = []
            for vehicleID, spawnTime in self.__cloneSpawnTimes.iteritems():
                lifeTime = self.__cloneLifeTimes.get(vehicleID, 0)
                remaining = math.ceil(lifeTime - (now - spawnTime))
                if remaining <= 0:
                    expiredTimers.append(vehicleID)
                    remaining = 0
                self.__setCloneRemainingTime(vehicleID, remaining)

            for vehicleID in expiredTimers:
                self.__cloneSpawnTimes.pop(vehicleID, None)
                self.__cloneLifeTimes.pop(vehicleID, None)
                self.__cloneRemainingTimes.pop(vehicleID, None)

            self.__ensureCloneTimer()
            return

    def __setCloneRemainingTime(self, vehicleID, remaining):
        remaining = int(remaining)
        marker = self._markers.get(vehicleID)
        if marker is None:
            return
        elif self.__cloneRemainingTimes.get(vehicleID, 0) == remaining:
            return
        else:
            self.__cloneRemainingTimes[vehicleID] = remaining
            markerText = backport.text(R.strings.ingame_gui.wt_clone.cloneRemainingTime(), remainingTime=remaining)
            self._invokeMarker(marker.getMarkerID(), 'setAbilityDurationValue', markerText)
            return

    def __dropCloneTimer(self, vehicleID):
        if vehicleID in self.__cloneSpawnTimes:
            self.__cloneSpawnTimes.pop(vehicleID, None)
            self.__cloneLifeTimes.pop(vehicleID, None)
            self.__setCloneRemainingTime(vehicleID, 0)
            self.__cloneRemainingTimes.pop(vehicleID, None)
            self.__ensureCloneTimer()
        return

    def __isBossWithPlasma(self, vInfo):
        vehicle = BigWorld.entities.get(vInfo.vehicleID)
        return False if not vehicle else 'wtExtractorShot' in vehicle.dynamicComponents


class WhiteTigerEventBusPlugin(EventBusPlugin):

    def start(self):
        super(WhiteTigerEventBusPlugin, self).start()
        teleport = self.sessionProvider.dynamic.teleport
        if teleport is not None:
            teleport.onShowSpawnPoints += self._onShowSpawnPoints
            teleport.onCloseSpawnPoints += self._onCloseSpawnPoints
        return

    def stop(self):
        teleport = self.sessionProvider.dynamic.teleport
        if teleport is not None:
            teleport.onShowSpawnPoints -= self._onShowSpawnPoints
            teleport.onCloseSpawnPoints -= self._onCloseSpawnPoints
        super(WhiteTigerEventBusPlugin, self).stop()
        return

    def _onShowSpawnPoints(self, *_):
        self._parentObj.setVisible(False)

    def _onCloseSpawnPoints(self, *_):
        self._parentObj.setVisible(True)


class WhiteTigerBaseAreaMarkerPlugin(AreaMarkerPlugin, ChatCommunicationComponent):
    __slots__ = ('__markers', '__entityMap', '__clazz')

    def __init__(self, parentObj, clazz=BaseMarker):
        super(WhiteTigerBaseAreaMarkerPlugin, self).__init__(parentObj)
        self.__markers = {}
        self.__clazz = clazz
        self.__entityMap = {}
        ChatCommunicationComponent.__init__(self, parentObj)

    def start(self):
        super(WhiteTigerBaseAreaMarkerPlugin, self).start()
        ChatCommunicationComponent.start(self)

    def stop(self):
        self.__markers = {}
        ChatCommunicationComponent.stop(self)
        super(WhiteTigerBaseAreaMarkerPlugin, self).stop()

    def createMarker(self, uniqueID, matrixProvider, active, symbol=settings.MARKER_SYMBOL_NAME.STATIC_OBJECT_MARKER):
        if uniqueID in self.__markers:
            return False
        markerID = self._createMarkerWithMatrix(symbol, matrixProvider, active=active)
        marker = self.__clazz(markerID, True)
        self.__markers[uniqueID] = marker
        marker.setState(ReplyStateForMarker.NO_ACTION)
        self._setActiveState(marker, marker.getState())
        self.__addActiveCommandsOnMarker(uniqueID)
        return True

    def mapCustomEntityID(self, uniqueID, entityID):
        self.__entityMap[uniqueID] = entityID

    def deleteCustomEntityID(self, uniqueID):
        if uniqueID in self.__entityMap:
            self.__entityMap.pop(uniqueID)

    def deleteMarker(self, uniqueID):
        markerID = self.__markers.pop(uniqueID, None)
        if markerID is not None:
            self._destroyMarker(markerID.getMarkerID())
            return True
        else:
            return False

    def setupMarker(self, uniqueID, shape, minDistance, maxDistance, distance, metersString, distanceFieldColor):
        if uniqueID not in self.__markers:
            return
        self._invokeMarker(self.__markers[uniqueID].getMarkerID(), 'init', shape, minDistance, maxDistance, distance, metersString, distanceFieldColor)

    def markerSetDistance(self, uniqueID, distance):
        if uniqueID not in self.__markers:
            return
        self._invokeMarker(self.__markers[uniqueID].getMarkerID(), 'setDistance', distance)

    def setMarkerMatrix(self, uniqueID, matrix):
        markerID = self.__markers.pop(uniqueID, None)
        if markerID is None:
            return
        else:
            self._parentObj.setMarkerMatrix(markerID, matrix)
            return

    def invokeMarker(self, uniqueID, name, *args):
        if uniqueID in self.__markers:
            self._setActiveState(self.__markers[uniqueID], ReplyStateForMarker.CREATE_STATE)
            self._invokeMarker(self.__markers[uniqueID].getMarkerID(), name, *args)

    def setMarkerRenderInfo(self, uniqueID, minScale, offset, innerOffset, cullDistance, boundsMinScale):
        if uniqueID in self.__markers:
            self._setMarkerRenderInfo(self.__markers[uniqueID].getMarkerID(), minScale, offset, innerOffset, cullDistance, boundsMinScale)

    def setMarkerSticky(self, uniqueID, isSticky):
        if uniqueID in self.__markers:
            self._setMarkerSticky(self.__markers[uniqueID].getMarkerID(), isSticky)

    def setMarkerLocationOffset(self, uniqueID, minYOffset, maxYOffset, distanceForMinYOffset, maxBoost, boostStart):
        if uniqueID in self.__markers:
            self._setMarkerLocationOffset(self.__markers[uniqueID].getMarkerID(), minYOffset, maxYOffset, distanceForMinYOffset, maxBoost, boostStart)

    def setMarkerBoundEnabled(self, markerID, isBoundEnabled):
        if markerID in self.__markers:
            self._setMarkerBoundEnabled(self.__markers[markerID].getMarkerID(), isBoundEnabled)

    def getMarkerType(self):
        return MarkerType.BASE_MARKER_TYPE

    def getMarkerIdFromEntityID(self, entityID, markerType):
        for entityIDEntry in self.__entityMap:
            if self.__entityMap[entityIDEntry] == entityID and markerType == self.getMarkerType():
                return entityIDEntry

        return INVALID_MARKER_ID

    def getTargetIDFromMarkerID(self, markerID):
        for baseID, marker in self.__markers.iteritems():
            if marker.getMarkerID() == markerID:
                return self.__entityMap[baseID]

        return INVALID_MARKER_ID

    def getMarkerSubtype(self, targetID):
        return INVALID_MARKER_SUBTYPE if targetID == INVALID_MARKER_ID else DefaultMarkerSubType.ENEMY_MARKER_SUBTYPE

    def _getMarkerFromTargetID(self, baseID, markerType):
        targetID = self.getMarkerIdFromEntityID(baseID, markerType)
        return None if targetID not in self.__markers else self.__markers[targetID]

    def __addActiveCommandsOnMarker(self, markerId):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is None:
            return
        else:
            cmdData = advChatCmp.getCommandDataForTargetIDAndMarkerType(markerId, MarkerType.BASE_MARKER_TYPE)
            if cmdData:
                marker = self.__markers[markerId]
                isPlayerSender = avatar_getter.getPlayerVehicleID() in cmdData.owners
                countNumber = len(cmdData.owners)
                marker.setIsSticky(isPlayerSender)
                self._setMarkerRepliesAndCheckState(marker, countNumber, isPlayerSender)
            return
