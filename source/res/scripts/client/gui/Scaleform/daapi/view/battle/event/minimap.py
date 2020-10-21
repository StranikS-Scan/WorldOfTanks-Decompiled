# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/minimap.py
from collections import namedtuple
from functools import partial
import logging
import BigWorld
import BattleReplay
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.radar_ctrl import IRadarListener
import Math
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.Scaleform.daapi.view.battle.shared.minimap.common import EntriesPlugin
from gui.battle_control import minimap_utils
from gui.Scaleform.daapi.view.battle.shared.minimap.entries import VehicleEntry
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import ArenaVehiclesPlugin, MinimapPingPlugin, _BASE_PING_RANGE, _LOCATION_PING_RANGE
from gui.Scaleform.daapi.view.battle.event.markers import EventBaseMinimapMarker
from gui.Scaleform.genConsts.BATTLE_MINIMAP_CONSTS import BATTLE_MINIMAP_CONSTS
from gui.Scaleform.daapi.view.battle.event.components import EventTargetMarkerUpdateComponent, EventGoalUpdateComponent, EventECPUpdateComponent
from chat_commands_consts import INVALID_MARKER_ID
from ids_generators import Int32IDGenerator
from helpers import isPlayerAvatar
from chat_commands_consts import MarkerType, ReplyState, BATTLE_CHAT_COMMAND_NAMES
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME
_LOOT_AMMO_SYMBOL_NAME = 'TutorialTargetMinimapEntryUI'
_logger = logging.getLogger(__name__)

class BotAppearNotificationPlugin(EntriesPlugin):
    __slots__ = ('__callbackIDs', '__idGenerator')
    _ANIMATION_NAME = 'firstEnemy'
    _MINIMAP_NOTIFICATION_DURATION = 3

    def __init__(self, parent):
        super(BotAppearNotificationPlugin, self).__init__(parent, clazz=VehicleEntry)
        self.__callbackIDs = {}
        self.__idGenerator = Int32IDGenerator()

    def stop(self):
        self.__clearAllCallbacks()
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onVehicleSpawnNotification -= self.__onVehicleSpawnNotification
        super(BotAppearNotificationPlugin, self).stop()

    def start(self):
        super(BotAppearNotificationPlugin, self).start()
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onVehicleSpawnNotification += self.__onVehicleSpawnNotification

    def __onVehicleSpawnNotification(self, position):
        matrix = minimap_utils.makePositionMatrix(position)
        uniqueID = self.__idGenerator.next()
        model = self._addEntryEx(uniqueID, _S_NAME.VEHICLE, _C_NAME.ALIVE_VEHICLES, matrix=matrix, active=True)
        self._invoke(model.getID(), 'setVehicleInfo', '', '', '', '', self._ANIMATION_NAME)
        self._playSound2D(settings.MINIMAP_ATTENTION_SOUND_ID)
        self.__scheduleCleanup(uniqueID, self._MINIMAP_NOTIFICATION_DURATION)

    def __scheduleCleanup(self, uniqueID, interval):
        self.__clearCallback(uniqueID)
        self.__callbackIDs[uniqueID] = BigWorld.callback(interval, partial(self.__clearCallback, uniqueID))

    def __clearCallback(self, uniqueID):
        callbackID = self.__callbackIDs.pop(uniqueID, None)
        if callbackID is not None:
            self._delEntryEx(uniqueID)
            BigWorld.cancelCallback(callbackID)
        return

    def __clearAllCallbacks(self):
        for uniqueID, callbackID in self.__callbackIDs.iteritems():
            self._delEntryEx(uniqueID)
            BigWorld.cancelCallback(callbackID)

        self.__callbackIDs.clear()


class LootObjectsEntriesPlugin(EntriesPlugin):
    __slots__ = ('_lootDict',)

    def __init__(self, parentObj):
        super(LootObjectsEntriesPlugin, self).__init__(parentObj)
        self._lootDict = {}

    def start(self):
        super(LootObjectsEntriesPlugin, self).start()
        self._updateCurrentOpacity()
        lootComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'loot', None)
        if lootComp is not None:
            lootComp.onLootAdded += self.__onLootAdded
            lootComp.onLootRemoved += self.__onLootRemoved
            lootEntities = lootComp.getLootEntities()
            for loot in lootEntities.values():
                self.__onLootAdded(loot)

        return

    def fini(self):
        lootComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'loot', None)
        if lootComp is not None:
            lootComp.onLootAdded -= self.__onLootAdded
            lootComp.onLootRemoved -= self.__onLootRemoved
        super(LootObjectsEntriesPlugin, self).fini()
        return

    def _updateCurrentOpacity(self):
        pass

    def _setLootHighlight(self, lootEntryID):
        self._invoke(lootEntryID, 'setHighlight', False)

    def __onLootRemoved(self, loot):
        if loot.id in self._lootDict:
            self._delEntry(self._lootDict[loot.id])
            del self._lootDict[loot.id]

    def __onLootAdded(self, loot):
        minimapSymbol = loot.gameObject.minimapSymbol
        if minimapSymbol is not None:
            matrix = Math.Matrix()
            matrix.setTranslate(loot.position)
            lootEntryID = self._addEntry(minimapSymbol, _C_NAME.ICONS, matrix=matrix, active=True)
            self._lootDict[loot.id] = lootEntryID
            if minimapSymbol == _LOOT_AMMO_SYMBOL_NAME:
                self._setLootHighlight(lootEntryID)
        return


RadarEntryParams = namedtuple('RadarEntryParams', 'symbol container')
RadarPluginParams = namedtuple('RadarPluginParams', 'fadeIn fadeOut lifetime vehicleEntryParams')

class _RadarEntryData(object):

    def __init__(self, entryId, destroyMeCallback, lifeTime, typeId=None):
        super(_RadarEntryData, self).__init__()
        self.__entryId = entryId
        self.__lifeTime = lifeTime
        self.__destroyMeCallback = destroyMeCallback
        self.__typeId = typeId
        self.__timerId = None
        return

    @property
    def entryId(self):
        return self.__entryId

    def getTypeId(self):
        return self.__typeId

    def destroy(self):
        self.stopTimer()
        self.__timerId = None
        self.__destroyMeCallback = None
        return

    def upTimer(self):
        self.stopTimer()
        self.__timerId = BigWorld.callback(self.__lifeTime, partial(self.__destroyMeCallback, self.__entryId))

    def stopTimer(self):
        if self.__timerId is not None:
            BigWorld.cancelCallback(self.__timerId)
        return


class RadarPlugin(EntriesPlugin, IRadarListener):
    _NOTIFICATION_DURATION = 3
    _ANIMATION_NAME = 'firstEnemy'

    def __init__(self, parent):
        super(RadarPlugin, self).__init__(parent)
        self._vehicleEntries = {}
        self._params = RadarPluginParams(fadeIn=0.0, fadeOut=0.0, lifetime=0.0, vehicleEntryParams=RadarEntryParams(container='', symbol=''))
        self._callbackIDs = {}

    def init(self, arenaVisitor, arenaDP):
        super(RadarPlugin, self).init(arenaVisitor, arenaDP)
        if self.sessionProvider.dynamic.radar:
            self.sessionProvider.dynamic.radar.addRuntimeView(self)

    def fini(self):
        self._clearAllCallbacks()
        if self.sessionProvider.dynamic.radar:
            self.sessionProvider.dynamic.radar.removeRuntimeView(self)
        super(RadarPlugin, self).fini()

    def radarInfoReceived(self, duration, positions):
        for _id, _pos in positions:
            self._addVehicleEntry(_id, _pos, duration)

        self._playSound2D(settings.MINIMAP_ATTENTION_SOUND_ID)

    def _addVehicleEntry(self, vehicleID, position, duration):
        matrix = minimap_utils.makePositionMatrix(position)
        model = self._addEntryEx(vehicleID, _S_NAME.VEHICLE, _C_NAME.ALIVE_VEHICLES, matrix=matrix, active=True)
        self._invoke(model.getID(), 'setVehicleInfo', vehicleID, '', '', '', self._ANIMATION_NAME)
        self._scheduleCleanup(vehicleID, duration)

    def _scheduleCleanup(self, vehicleID, interval):
        self._clearCallback(vehicleID)
        self._callbackIDs[vehicleID] = BigWorld.callback(interval, partial(self._clearCallback, vehicleID))

    def _clearCallback(self, vehicleID):
        callbackID = self._callbackIDs.pop(vehicleID, None)
        if callbackID is not None:
            self._delEntryEx(vehicleID)
            BigWorld.cancelCallback(callbackID)
        return

    def _clearAllCallbacks(self):
        for uniqueID, callbackID in self._callbackIDs.iteritems():
            self._delEntryEx(uniqueID)
            BigWorld.cancelCallback(callbackID)

        self._callbackIDs.clear()


class EventControlPointEntriesPlugin(EntriesPlugin, EventGoalUpdateComponent, EventECPUpdateComponent, EventTargetMarkerUpdateComponent, GameEventGetterMixin):

    def __init__(self, parentObj):
        super(EventControlPointEntriesPlugin, self).__init__(parentObj)
        GameEventGetterMixin.__init__(self)
        self._markers = {}

    def start(self):
        super(EventControlPointEntriesPlugin, self).start()
        EventECPUpdateComponent.start(self)
        EventGoalUpdateComponent.start(self)
        EventTargetMarkerUpdateComponent.start(self)
        self.environmentData.onEnvironmentEventIDUpdate += self.__onEventEnvironmentUpdate
        self._restart()

    def stop(self):
        EventGoalUpdateComponent.stop(self)
        EventECPUpdateComponent.stop(self)
        EventTargetMarkerUpdateComponent.stop(self)
        self._markers.clear()
        super(EventControlPointEntriesPlugin, self).stop()
        self.environmentData.onEnvironmentEventIDUpdate -= self.__onEventEnvironmentUpdate

    def _restart(self):
        EventECPUpdateComponent._restart(self)
        EventGoalUpdateComponent._restart(self)
        EventTargetMarkerUpdateComponent._restart(self)

    def getTargetIDFromMarkerID(self, markerID):
        for ecpID, marker in self._markers.iteritems():
            if markerID == marker.getMarkerID():
                return ecpID

        return INVALID_MARKER_ID

    def _getMarkerFromTargetID(self, targetID, markerType):
        return None if targetID not in self._markers else self._markers[targetID]

    def _invokeMarker(self, markerID, function, *args):
        if function == BATTLE_MINIMAP_CONSTS.SET_STATE and args[0] == BATTLE_MINIMAP_CONSTS.STATE_DEFAULT:
            ecpID = self.getTargetIDFromMarkerID(markerID)
            if ecpID != INVALID_MARKER_ID and self._markers[ecpID].getIsReplied():
                return
        self._invoke(markerID, function, *args)

    def _setDistanceToObject(self, marker):
        pass

    def _setMarkerActive(self, markerID, shouldNotHide):
        self._setActive(markerID, shouldNotHide)

    def _destroyMarker(self, markerID):
        ecpID = self.getTargetIDFromMarkerID(markerID)
        if ecpID != -1:
            self._delEntryEx(ecpID)

    def _addCampOrControlPointMarker(self, symbol, position, ecpID):
        minimapSymbol = EventBaseMinimapMarker.MARKER_SYMBOLS[symbol]
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        model = self._addEntryEx(ecpID, minimapSymbol, _C_NAME.ICONS, matrix=matrix, active=True)
        isVolot = minimapSymbol.startswith((EventBaseMinimapMarker.VOLOT_SYMBOL,))
        marker = EventBaseMinimapMarker(model.getID(), True, 'ally' if isVolot else 'enemy')
        marker.setSymbol(minimapSymbol)
        marker.setPosition(position)
        self._setActive(marker.getMarkerID(), False if isVolot else True)
        self._markers[ecpID] = marker

    def __onEventEnvironmentUpdate(self, eventEnvID):
        if eventEnvID:
            self._restart()


class EventArenaVehiclesPlugin(ArenaVehiclesPlugin, GameEventGetterMixin):

    def __init__(self, parent):
        super(EventArenaVehiclesPlugin, self).__init__(parent)
        GameEventGetterMixin.__init__(self)
        self.__bossEntryID = None
        return

    def start(self):
        super(EventArenaVehiclesPlugin, self).start()
        self.environmentData.onEnvironmentEventIDUpdate += self.__onEnvironmentEventIDUpdate
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onBotRolesReceived += self.__onBotRolesReceived

    def stop(self):
        self.environmentData.onEnvironmentEventIDUpdate -= self.__onEnvironmentEventIDUpdate
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onBotRolesReceived -= self.__onBotRolesReceived
        super(EventArenaVehiclesPlugin, self).stop()

    def updateControlMode(self, mode, vehicleID):
        prevCtrlID = self._ctrlVehicleID
        super(EventArenaVehiclesPlugin, self).updateControlMode(mode, vehicleID)
        if self._isInRespawnDeath():
            self.eventSwitchToVehicle(prevCtrlID)

    def _getClassTag(self, vInfo):
        player = BigWorld.player()
        if player.team == vInfo.team:
            return super(EventArenaVehiclesPlugin, self)._getClassTag(vInfo)
        vehicleID = vInfo.vehicleID
        if player.isBoss(vehicleID):
            self.__bossEntryID = vehicleID
        return player.getBotRole(vehicleID)

    def __onBotRolesReceived(self):
        player = BigWorld.player()
        updated = ((0, vInfo) for vInfo in self._arenaDP.getVehiclesInfoIterator() if player.team != vInfo.team)
        self.updateVehiclesInfo(updated, self._arenaDP)

    def __onEnvironmentEventIDUpdate(self, _):
        if self.__bossEntryID:
            bossEntry = self._entries.get(self.__bossEntryID)
            if bossEntry:
                bossEntry.setActive(False)
                self._setActive(bossEntry.getID(), False)
                self.__bossEntryID = None
        return


class EventMinimapPingPlugin(MinimapPingPlugin):

    def _getClickPosition(self, x, y):
        return minimap_utils.makePointMatrixByLocal(x, y, *self._boundingBox).translation

    def _getIdByBaseNumber(self, team, number):
        pass

    def _processCommandByPosition(self, commands, locationCommand, position, minimapScaleIndex):
        if avatar_getter.isVehicleAlive():
            ecp = self._getNearestECPIDForPosition(position, _BASE_PING_RANGE)
            if ecp is not None:
                self._make3DPingECP(commands, ecp)
                return
            locationID = self._getNearestLocationIDForPosition(position, _LOCATION_PING_RANGE)
            if locationID is not None:
                self._replyPing3DMarker(commands, locationID)
                return
        commands.sendAttentionToPosition3D(position, locationCommand)
        return

    def _getNearestECPIDForPosition(self, inPosition, range_):
        minVal = None
        battleMarkersCtrl = self.sessionProvider.dynamic.battleMarkers
        if battleMarkersCtrl is None:
            return minVal
        else:
            for targetID, position, symbol in battleMarkersCtrl.getECPPositionsIterator():
                if minVal is None:
                    minVal = (targetID, position, symbol)
                    continue
                if Math.Vector3(position).flatDistTo(inPosition) < Math.Vector3(minVal[1]).flatDistTo(inPosition):
                    minVal = (targetID, position, symbol)

            if minVal is None:
                return
            return minVal if Math.Vector3(minVal[1]).flatDistTo(inPosition) <= range_ else None

    def _make3DPingECP(self, commands, ecp):
        advChatCmp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is None:
            return
        else:
            targetID, _, symbol = ecp
            replyState, commandKey = advChatCmp.getReplyStateForTargetIDAndMarkerType(targetID, MarkerType.BASE_MARKER_TYPE)
            if replyState is ReplyState.NO_REPLY:
                commandKey = BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE if symbol != 'SoulCollector' else BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE
                commands.sendCommandToBase(targetID, commandKey, symbol)
                return
            self._processReplyCommand(replyState, commands, targetID, commandKey)
            return


class EventMinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(EventMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['bot_appear_notification'] = BotAppearNotificationPlugin
        setup['loot_objects'] = LootObjectsEntriesPlugin
        setup['radar'] = RadarPlugin
        setup['ecp'] = EventControlPointEntriesPlugin
        setup['vehicles'] = EventArenaVehiclesPlugin
        if not BattleReplay.g_replayCtrl.isPlaying:
            setup['pinging'] = EventMinimapPingPlugin
        return setup
