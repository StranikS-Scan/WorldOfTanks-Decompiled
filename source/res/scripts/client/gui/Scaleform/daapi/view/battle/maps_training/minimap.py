# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/maps_training/minimap.py
import BigWorld
from helpers import isPlayerAvatar
from account_helpers.settings_core.settings_constants import GAME
from vehicle_systems.stricted_loading import makeCallbackWeak
from items.vehicles import getVehicleClassFromVehicleType
from battleground.location_point_manager import g_locationPointManager
from chat_commands_consts import MarkerType, LocationMarkerSubType
from gui import GUI_SETTINGS
from gui.battle_control import minimap_utils, matrix_factory
from gui.battle_control.battle_constants import PLAYER_GUI_PROPS
from gui.Scaleform.daapi.view.battle.shared.minimap import common, settings, plugins
from gui.Scaleform.daapi.view.battle.shared.minimap.entries import VehicleEntry
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent, GlobalSettingsPlugin
_C_NAME = settings.CONTAINER_NAME
_LOCATION_PING_RANGE = 30
_MINIMAP_MIN_SCALE_INDEX = 0
_MINIMAP_MAX_SCALE_INDEX = 5
_MINIMAP_SIZE_SETTING = 'mapsTrainingMinimapSize'
_MINIMAP_ENTRY_DEAD_TIME = 1
_MINIMAP_LOCATION_MARKER_MIN_SCALE = 1.0
_MINIMAP_LOCATION_MARKER_MAX_SCALE = 0.72
_ANIMATION_NAME = 'firstEnemy'
_LOCATION_SUBTYPE_TO_FLASH_SYMBOL_NAME = {LocationMarkerSubType.VEHICLE_SPOTPOINT_SUBTYPE: 'MapsTrainingVehicleEntryUI'}

class MapsTrainingVehicleEntry(VehicleEntry):
    __slots__ = ('_isPlayerAtAim', '_isGoal', '_vehicleID')

    def __init__(self, entryID, active, matrix=None):
        super(MapsTrainingVehicleEntry, self).__init__(entryID, active, matrix=matrix)
        self._isPlayerAtAim = False
        self._isGoal = False
        self._vehicleID = 0

    def setPlayerAtAim(self, isPlayerAtAim):
        self._isPlayerAtAim = isPlayerAtAim

    def setGoalForPlayer(self, isGoal):
        self._isGoal = isGoal

    def isPlayerAtAim(self):
        return self._isPlayerAtAim

    def isGoalForPlayer(self):
        return self._isGoal

    def setOwnVehicleID(self, vehicleID):
        self._vehicleID = vehicleID

    def getOwnVehicleID(self):
        return self._vehicleID


class BotAppearNotificationPlugin(common.EntriesPlugin):

    def __init__(self, parent):
        super(BotAppearNotificationPlugin, self).__init__(parent, clazz=MapsTrainingVehicleEntry)
        self._curScale = 1.0
        self.__localGoals = set()
        self.__callbacksIDs = {}

    def stop(self):
        while self.__callbacksIDs:
            _, callbackID = self.__callbacksIDs.popitem()
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded -= self.__addSpottedVehicleStaticMarker
            ctrl.onStaticMarkerRemoved -= self.__removeSpottedVehicleStaticMarker
            ctrl.onReplyFeedbackReceived -= self.__updateSpottedVehicleStaticMarker
            ctrl.onLocalKillGoalsUpdated -= self.__onLocalKillGoalsUpdated
            ctrl.onMinimapVehicleAdded -= self.__onMinimapVehicleAdded
            ctrl.onMinimapVehicleRemoved -= self.__onMinimapVehicleRemoved
        self.__localGoals = set()
        if isPlayerAvatar():
            arena = BigWorld.player().arena
            if arena is not None:
                arena.onVehicleKilled -= self.__onArenaVehicleKilled
        super(BotAppearNotificationPlugin, self).stop()
        return

    def start(self):
        super(BotAppearNotificationPlugin, self).start()
        minimapSize = settings.clampMinimapSizeIndex(self.settingsCore.getSetting(GAME.MINIMAP_SIZE))
        self._curScale = self._calculateMarkerScale(minimapSize)
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onStaticMarkerAdded += self.__addSpottedVehicleStaticMarker
            ctrl.onStaticMarkerRemoved += self.__removeSpottedVehicleStaticMarker
            ctrl.onReplyFeedbackReceived += self.__updateSpottedVehicleStaticMarker
            ctrl.onLocalKillGoalsUpdated += self.__onLocalKillGoalsUpdated
            ctrl.onMinimapVehicleAdded += self.__onMinimapVehicleAdded
            ctrl.onMinimapVehicleRemoved += self.__onMinimapVehicleRemoved
        if isPlayerAvatar():
            arena = BigWorld.player().arena
            if arena is not None:
                arena.onVehicleKilled += self.__onArenaVehicleKilled
        return

    def _getModel(self, targetID):
        return self._entries.get(targetID)

    def __addSpottedVehicleStaticMarker(self, areaID, creatorID, position, locationMarkerSubtype, markerText='', numberOfReplies=0, isTargetForPlayer=False):
        if locationMarkerSubtype not in _LOCATION_SUBTYPE_TO_FLASH_SYMBOL_NAME:
            return
        matrix = minimap_utils.makePositionAndScaleMatrix(position, (self._curScale, 1.0, self._curScale))
        model = self._addEntryEx(areaID, _LOCATION_SUBTYPE_TO_FLASH_SYMBOL_NAME[locationMarkerSubtype], _C_NAME.ALIVE_VEHICLES, matrix=matrix, active=True)
        model.setOwnVehicleID(int(markerText) if markerText else 0)
        vehInfo = self._arenaVisitor.vehicles.getVehicleInfo(model.getOwnVehicleID())
        classTag = getVehicleClassFromVehicleType(vehInfo['vehicleType'].type)
        guiProps = PLAYER_GUI_PROPS.enemy
        model.setVehicleInfo(not guiProps.isFriend, guiProps.name(), classTag, True)
        model.setInAoI(False)
        model.setGoalForPlayer(model.getOwnVehicleID() in self.__localGoals)
        self.__updateVehInfo(areaID, False)
        self._setActive(model.getID(), True)
        self._playSound2D(settings.MINIMAP_ATTENTION_SOUND_ID)

    def __updateSpottedVehicleStaticMarker(self, targetID, replierVehicleID, markerType, oldReplyCount, newReplycount):
        model = self._getModel(targetID)
        if model is None or replierVehicleID != self._arenaVisitor.getArenaUniqueID() or markerType != MarkerType.LOCATION_MARKER_TYPE:
            return
        else:
            model.setPlayerAtAim(oldReplyCount < newReplycount)
            self.__updateVehInfo(targetID, True)
            return

    def __updateVehInfo(self, targetID, wasSpotted=True):
        model = self._getModel(targetID)
        if model is None:
            return
        else:
            self._invoke(model.getID(), 'setState', self._getCombinedModelStates(model))
            self._invoke(model.getID(), 'setVehicleInfo', targetID, model.getClassTag(), '', model.getGUILabel(), '' if wasSpotted else _ANIMATION_NAME)
            self._invoke(model.getID(), 'setInAoI', model.isInAoI())
            return

    def __removeSpottedVehicleStaticMarker(self, targetID):
        callbackID = self.__callbacksIDs.pop(targetID, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        model = self._entries.get(targetID)
        if model is not None:
            self._move(model.getID(), _C_NAME.DEAD_VEHICLES)
            self._delEntryEx(targetID)
        return

    def __onLocalKillGoalsUpdated(self, localGoals):
        self.__localGoals = set((vID for vID in localGoals))
        for targetID, model in self._entries.iteritems():
            model.setGoalForPlayer(model.getOwnVehicleID() in self.__localGoals)
            self.__updateVehInfo(targetID, True)

    def __onArenaVehicleKilled(self, victimID, attackerID, equipmentID, reason, numVehiclesAffected):
        for targetID, model in self._entries.iteritems():
            if victimID == model.getOwnVehicleID() and targetID not in self.__callbacksIDs:
                model.setAlive(False)
                if GUI_SETTINGS.showMinimapDeath and not GUI_SETTINGS.permanentMinimapDeath:
                    self._invoke(model.getID(), 'setDead', False)
                    self.__callbacksIDs[targetID] = BigWorld.callback(_MINIMAP_ENTRY_DEAD_TIME, makeCallbackWeak(self.__removeSpottedVehicleStaticMarker, targetID))
                else:
                    self.__removeSpottedVehicleStaticMarker(targetID)
                break

    def __onMinimapVehicleAdded(self, vProxy, vInfo, guiProps):
        if vProxy.isAlive():
            self.__switchVehicleVisualState(vInfo.vehicleID, True)

    def __onMinimapVehicleRemoved(self, vehicleID):
        self.__switchVehicleVisualState(vehicleID, False)

    def __switchVehicleVisualState(self, vehicleID, isVisualStarted):
        for targetID, model in self._entries.iteritems():
            if vehicleID == model.getOwnVehicleID():
                model.setInAoI(isVisualStarted)
                self.__setVehicleMatrixAndLocation(model, vehicleID, self._arenaVisitor.getArenaPositions())
                self.__updateVehInfo(targetID, not isVisualStarted)
                break

    def __setVehicleMatrixAndLocation(self, model, vehicleID, positions):
        matrix, location = matrix_factory.getVehicleMPAndLocation(vehicleID, positions)
        model.setLocation(location)
        if matrix is not None:
            model.setMatrix(matrix)
            self._setMatrix(model.getID(), matrix)
        return

    @staticmethod
    def _calculateMarkerScale(minimapSizeIndex):
        p = float(minimapSizeIndex - _MINIMAP_MIN_SCALE_INDEX) / float(_MINIMAP_MAX_SCALE_INDEX - _MINIMAP_MIN_SCALE_INDEX)
        return (1 - p) * _MINIMAP_LOCATION_MARKER_MIN_SCALE + p * _MINIMAP_LOCATION_MARKER_MAX_SCALE

    @staticmethod
    def _getCombinedModelStates(entry):
        return int(entry.isPlayerAtAim()) | int(entry.isGoalForPlayer() and entry.isInAoI()) << 1


class MapsTrainingGlobalSettingsPlugin(GlobalSettingsPlugin):

    def __init__(self, parentObj):
        super(MapsTrainingGlobalSettingsPlugin, self).__init__(parentObj)
        self._changeSizeSettings(_MINIMAP_SIZE_SETTING)


class MapsTrainingAreaStaticMarkerPlugin(plugins.AreaStaticMarkerPlugin):
    __slots__ = ()

    def _onReplyFeedbackReceived(self, ucmdID, replierID, markerType, oldReplyCount, newReplyCount):
        locationPoints = g_locationPointManager.markedAreas
        return False if not locationPoints or ucmdID not in locationPoints or locationPoints[ucmdID].creatorID == self._arenaVisitor.getArenaUniqueID() else super(MapsTrainingAreaStaticMarkerPlugin, self)._onReplyFeedbackReceived(ucmdID, replierID, markerType, oldReplyCount, newReplyCount)


class MapsTrainingMinimapComponent(ClassicMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(MapsTrainingMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['settings'] = MapsTrainingGlobalSettingsPlugin
        setup['vehicles'] = BotAppearNotificationPlugin
        setup['area'] = MapsTrainingAreaStaticMarkerPlugin
        return setup
