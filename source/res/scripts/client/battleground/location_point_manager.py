# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/location_point_manager.py
import logging
from collections import namedtuple
import BigWorld
import Math
import ResMgr
from avatar_components.CombatEquipmentManager import CombatEquipmentManager
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES, MarkerType, LocationMarkerSubType, _DEFAULT_ACTIVE_COMMAND_TIME
from gui.battle_control import avatar_getter
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.stricted_loading import makeCallbackWeak
_logger = logging.getLogger(__name__)
_EquipmentAdapter = namedtuple('_EquipmentAdapter', ['areaWidth',
 'areaLength',
 'areaVisual',
 'areaColor',
 'areaMarker'])
_DYNAMIC_OBJECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'
_AREA_VISUAL_SECTION = {BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA: 'stunAreaVisual',
 BATTLE_CHAT_COMMAND_NAMES.SHOOTING_POINT: 'shootAreaVisual'}
_DIR_UP = Math.Vector3(0.0, 1.0, 0.0)
_STUN_AREA_DEFAULTS = {'radius': 15.0,
 'areasNum': 3,
 'color': '0xff000000',
 'visual': 'content/Interface/CheckPoint/CheckPoint_white.visual',
 'lineColor': '0x0ff00000',
 'lineWidth': 3.0,
 'lineHeight': 3.0}
_CHECK_DISTANCE_CALLBACK_TIME = 1.5
_DISTANCE_FOR_MARKER_REMOVAL = 15.0
COMMAND_NAME_TO_LOCATION_MARKER_SUBTYPE = {BATTLE_CHAT_COMMAND_NAMES.GOING_THERE: LocationMarkerSubType.GOING_TO_MARKER_SUBTYPE,
 BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION: LocationMarkerSubType.ATTENTION_TO_MARKER_SUBTYPE,
 BATTLE_CHAT_COMMAND_NAMES.PREBATTLE_WAYPOINT: LocationMarkerSubType.PREBATTLE_WAYPOINT_SUBTYPE,
 BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA: LocationMarkerSubType.SPG_AIM_AREA_SUBTYPE,
 BATTLE_CHAT_COMMAND_NAMES.VEHICLE_SPOTPOINT: LocationMarkerSubType.VEHICLE_SPOTPOINT_SUBTYPE,
 BATTLE_CHAT_COMMAND_NAMES.SHOOTING_POINT: LocationMarkerSubType.SHOOTING_POINT_SUBTYPE,
 BATTLE_CHAT_COMMAND_NAMES.NAVIGATION_POINT: LocationMarkerSubType.NAVIGATION_POINT_SUBTYPE}

class LocationPointData(object):

    def __init__(self, creatorID, position, targetID, commandID, replyCount, markerText, markerSubType):
        self.creatorID = creatorID
        self.position = position
        self.targetID = targetID
        self.commandID = commandID
        self.replyCount = replyCount
        self.markerText = markerText
        self.markerSubType = markerSubType
        self.areas = []


class LocationPointManager(CallbackDelayer):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(LocationPointManager, self).__init__()
        self.__markedAreas = dict()
        self.__activeLocationMarkerID = None
        self.__resources = {}
        self.__visualisationData = dict(((k, self.__getAreaParamsConfig(v)) for k, v in _AREA_VISUAL_SECTION.iteritems()))
        return

    def activate(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl:
            ctrl.onReplyFeedbackReceived += self.__onReplyFeedbackReceived
            ctrl.onRemoveCommandReceived += self.__onRemoveCommandReceived

    def deactivate(self):
        CallbackDelayer.destroy(self)
        ctrl = self.sessionProvider.shared.feedback
        if ctrl:
            ctrl.onReplyFeedbackReceived -= self.__onReplyFeedbackReceived
            ctrl.onRemoveCommandReceived -= self.__onRemoveCommandReceived
        removeIDList = self.__markedAreas.keys()
        for targetID in removeIDList:
            self.__removeMarkedArea(targetID)

    def loadPrerequisites(self):
        prereqs = []
        for visualData in self.__visualisationData.iteritems():
            if 'visual' in visualData:
                prereqs.append(visualData['visual'])

        BigWorld.loadResourceListBG(prereqs, makeCallbackWeak(self.__onPrereqsLoaded))

    def addLocationPoint(self, position, targetID, creatorID, cmdID=None, activeTime=_DEFAULT_ACTIVE_COMMAND_TIME, markerText='', numberOfReplies=0, isTargetForPlayer=False):
        ctrl = self.sessionProvider.shared.feedback
        if not ctrl:
            _logger.warning('self.sessionProvider.shared.feedback is None')
            return
        else:
            if markerText is None:
                ctx = self.sessionProvider.getCtx()
                markerText = ctx.getPlayerFullName(creatorID, showVehShortName=False)
            commandName = _ACTIONS.battleChatCommandFromActionID(cmdID).name
            if targetID in self.__markedAreas:
                self.__removeMarkedArea(targetID)
            self.__markedAreas[targetID] = LocationPointData(creatorID, position, targetID, cmdID, numberOfReplies, markerText, COMMAND_NAME_TO_LOCATION_MARKER_SUBTYPE[commandName])
            if commandName in self.__visualisationData.keys():
                params = self.__visualisationData[commandName]
                isServerCommand = creatorID == self.sessionProvider.arenaVisitor.getArenaUniqueID()
                if isServerCommand and commandName == BATTLE_CHAT_COMMAND_NAMES.SHOOTING_POINT and markerText:
                    params = dict(((k, v if k != 'radius' else float(markerText)) for k, v in params.iteritems()))
                    markerText = ''
                self.__addVisualisationArea(targetID, position, params, not isServerCommand)
            if isTargetForPlayer:
                self.__activeLocationMarkerID = targetID
                self.delayCallback(_CHECK_DISTANCE_CALLBACK_TIME, self.__checkDistanceForRepliersCB)
            ctrl.onStaticMarkerAdded(targetID, creatorID, position, COMMAND_NAME_TO_LOCATION_MARKER_SUBTYPE[commandName], markerText, numberOfReplies, isTargetForPlayer)
            return

    def getLocationPointData(self, targetID):
        return self.__markedAreas.get(targetID, None)

    def setGUIVisible(self, visible):
        for _, locPointData in self.__markedAreas.iteritems():
            for area in locPointData.areas:
                area.setGUIVisible(visible)

    def getRepliablePoints(self, currPlayerID):
        result = []
        for point in self.__markedAreas.itervalues():
            commandName = _ACTIONS.battleChatCommandFromActionID(point.commandID).name
            if point.creatorID == currPlayerID and commandName == BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION:
                continue
            result.append(point)

        return result

    def __onPrereqsLoaded(self, resourceRefs):
        for chatCmd, params in self.__visualisationData.iteritems():
            if params['visual'] not in resourceRefs.failedIDs:
                self.__resources[chatCmd] = resourceRefs
            _logger.warning('Resource is not found: %s', self.__resources['visual'])

    def __removeMarkedArea(self, targetID):
        if targetID in self.__markedAreas:
            markerData = self.__markedAreas[targetID]
            for area in markerData.areas:
                if area is not None:
                    area.destroy()

            ctrl = self.sessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.onStaticMarkerRemoved(targetID)
            self.__markedAreas.pop(targetID)
        else:
            _logger.warning("Location area with ID %d doesn't exist!", targetID)
        return

    def __onReplyFeedbackReceived(self, targetID, replierID, markerType, oldReplyCount, newReplyCount):
        if markerType != MarkerType.LOCATION_MARKER_TYPE:
            return
        else:
            if targetID in self.__markedAreas:
                if replierID == avatar_getter.getPlayerVehicleID():
                    if self.__activeLocationMarkerID == targetID and oldReplyCount > newReplyCount:
                        self.__activeLocationMarkerID = None
                        self.stopCallback(self.__checkDistanceForRepliersCB)
                    else:
                        self.__activeLocationMarkerID = targetID
                        self.delayCallback(_CHECK_DISTANCE_CALLBACK_TIME, self.__checkDistanceForRepliersCB)
                self.__markedAreas[targetID].replyCount = newReplyCount
            return

    def __checkDistanceForRepliersCB(self):
        if self.__activeLocationMarkerID is None or self.__activeLocationMarkerID not in self.__markedAreas:
            return
        else:
            distanceToWaypoint = (self.__markedAreas[self.__activeLocationMarkerID].position - avatar_getter.getOwnVehiclePosition()).length
            if distanceToWaypoint < _DISTANCE_FOR_MARKER_REMOVAL:
                commandName = _ACTIONS.battleChatCommandFromActionID(self.__markedAreas[self.__activeLocationMarkerID].commandID).name
                targetID = self.__markedAreas[self.__activeLocationMarkerID].targetID
                commands = self.sessionProvider.shared.chatCommands
                if commands is not None:
                    commands.sendCancelReplyChatCommand(targetID, commandName)
            return _CHECK_DISTANCE_CALLBACK_TIME

    def __onRemoveCommandReceived(self, removeID, markerType):
        if markerType != MarkerType.LOCATION_MARKER_TYPE:
            return
        self.__removeMarkedArea(removeID)

    def __addVisualisationArea(self, targetID, position, visualisationParams, showArea=True):
        areas = []
        for i in xrange(0, visualisationParams['areasNum']):
            area = self.__createArea(position, visualisationParams, areaIndex=i)
            if area is not None:
                area.setGUIVisible(True)
                area.enableAccurateCollision(showArea)
                areas.append(area)

        self.__markedAreas[targetID].areas = areas
        return

    def __createArea(self, position, visualisationParams, areaIndex):
        markerRadius = visualisationParams['radius']
        offset = markerRadius / visualisationParams['areasNum']
        areaDiameter = 2.0 * (markerRadius - areaIndex * offset)
        adaptedAreaDesc = _EquipmentAdapter(areaDiameter, areaDiameter, visualisationParams['visual'], visualisationParams['color'], None)
        area = CombatEquipmentManager.createEquipmentSelectedArea(position, _DIR_UP, adaptedAreaDesc)
        return area

    @staticmethod
    def __getAreaParamsConfig(section):
        configSection = ResMgr.openSection(_DYNAMIC_OBJECTS_CONFIG_FILE)
        if configSection and configSection.has_key(section):
            configSection = configSection[section]
            return {'radius': configSection.readFloat('radius', _STUN_AREA_DEFAULTS['radius']),
             'areasNum': configSection.readInt('areasNum', _STUN_AREA_DEFAULTS['areasNum']),
             'color': int(configSection.readString('color', _STUN_AREA_DEFAULTS['color']), 0),
             'visual': configSection.readString('visual', _STUN_AREA_DEFAULTS['visual']),
             'lineColor': int(configSection.readString('lineColor', _STUN_AREA_DEFAULTS['lineColor']), 0),
             'lineWidth': configSection.readFloat('lineWidth', _STUN_AREA_DEFAULTS['lineWidth']),
             'lineHeight': configSection.readFloat('lineHeight', _STUN_AREA_DEFAULTS['lineHeight'])}
        return _STUN_AREA_DEFAULTS

    @property
    def markedAreas(self):
        return self.__markedAreas


g_locationPointManager = LocationPointManager()
