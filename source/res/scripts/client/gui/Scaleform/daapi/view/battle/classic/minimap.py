# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/minimap.py
import logging
import BattleReplay
import BigWorld
import CommandMapping
import Keys
import Math
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.settings_core import settings_constants
from chat_commands_consts import BATTLE_CHAT_COMMAND_NAMES, getBaseTeamAndIDFromUniqueID, MarkerType, getUniqueTeamOrControlPointID
from constants import IS_DEVELOPMENT
from debug_utils import LOG_DEBUG
from gui import GUI_SETTINGS, g_repeatKeyHandlers
from gui.Scaleform.daapi.view.battle.shared.minimap import common, plugins
from gui.Scaleform.daapi.view.battle.shared.minimap import component
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import _LOCATION_PING_RANGE, _BASE_PING_RANGE, _EMinimapMouseKey
from gui.Scaleform.genConsts.BATTLE_MINIMAP_CONSTS import BATTLE_MINIMAP_CONSTS
from gui.battle_control import minimap_utils, avatar_getter
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from messenger import MessengerEntry
from messenger.proto.bw_chat2.battle_chat_cmd import BASE_CMD_NAMES
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME
_logger = logging.getLogger(__name__)

class ClassicMinimapComponent(component.MinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(ClassicMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['settings'] = GlobalSettingsPlugin
        setup['points'] = TeamsOrControlsPointsPlugin
        if not BattleReplay.g_replayCtrl.isPlaying:
            setup['pinging'] = ClassicMinimapPingPlugin
        if IS_DEVELOPMENT:
            setup['teleport'] = ClassicTeleportPlugin
        return setup


class GlobalSettingsPlugin(common.SimplePlugin):
    __slots__ = ('__currentSizeSettings', '__isVisible', '__sizeIndex')
    _AccountSettingsClass = AccountSettings

    def __init__(self, parentObj):
        super(GlobalSettingsPlugin, self).__init__(parentObj)
        self.__currentSizeSettings = 'minimapSize'
        self.__isVisible = True
        self.__sizeIndex = 0

    def start(self):
        super(GlobalSettingsPlugin, self).start()
        if GUI_SETTINGS.minimapSize:
            g_eventBus.addListener(events.GameEvent.MINIMAP_CMD, self.__handleMinimapCmd, scope=EVENT_BUS_SCOPE.BATTLE)
            g_repeatKeyHandlers.add(self.__handleRepeatKeyEvent)

    def stop(self):
        if GUI_SETTINGS.minimapSize:
            g_eventBus.removeListener(events.GameEvent.MINIMAP_CMD, self.__handleMinimapCmd, scope=EVENT_BUS_SCOPE.BATTLE)
            g_repeatKeyHandlers.discard(self.__handleRepeatKeyEvent)
        super(GlobalSettingsPlugin, self).stop()

    def setSettings(self):
        newSize = settings.clampMinimapSizeIndex(self._AccountSettingsClass.getSettings(self.__currentSizeSettings))
        if self.__sizeIndex != newSize:
            self.__sizeIndex = newSize
            self._parentObj.as_setSizeS(self.__sizeIndex)
        self.__updateAlpha()

    def updateSettings(self, diff):
        if settings_constants.GAME.MINIMAP_ALPHA in diff or settings_constants.GAME.MINIMAP_ALPHA_ENABLED in diff:
            self.__updateAlpha()

    def applyNewSize(self, sizeIndex):
        LOG_DEBUG('Size index of minimap is changed', sizeIndex)
        self.__sizeIndex = sizeIndex
        self.__saveSettings()

    def _changeSizeSettings(self, newSizeSettings):
        if newSizeSettings == self.__currentSizeSettings:
            return newSizeSettings
        previousSettings = self.__currentSizeSettings
        self.__currentSizeSettings = newSizeSettings
        self.setSettings()
        return previousSettings

    def _toogleVisible(self):
        self.__isVisible = not self.__isVisible
        self._parentObj.as_setVisibleS(self.__isVisible)

    def __saveSettings(self):
        self._AccountSettingsClass.setSettings(self.__currentSizeSettings, self.__sizeIndex)

    def __setSizeByStep(self, step):
        newIndex = settings.clampMinimapSizeIndex(self.__sizeIndex + step)
        if self.__sizeIndex != newIndex:
            LOG_DEBUG('Try to change size index of minimap by step', newIndex)
            self._parentObj.as_setSizeS(newIndex)

    def __handleKey(self, key):
        if self._parentObj.isModalViewShown():
            return
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFired(CommandMapping.CMD_MINIMAP_SIZE_DOWN, key):
            self.__setSizeByStep(-1)
        elif cmdMap.isFired(CommandMapping.CMD_MINIMAP_SIZE_UP, key):
            self.__setSizeByStep(1)
        elif cmdMap.isFired(CommandMapping.CMD_MINIMAP_VISIBLE, key):
            self._toogleVisible()

    def __handleRepeatKeyEvent(self, event):
        if MessengerEntry.g_instance.gui.isFocused():
            return
        if event.isRepeatedEvent() and event.isKeyDown() and not BigWorld.isKeyDown(Keys.KEY_RSHIFT) and CommandMapping.g_instance.isFiredList((CommandMapping.CMD_MINIMAP_SIZE_DOWN, CommandMapping.CMD_MINIMAP_SIZE_UP), event.key):
            self.__handleKey(event.key)

    def __handleMinimapCmd(self, event):
        self.__handleKey(event.ctx['key'])

    def __updateAlpha(self):
        if self.settingsCore.getSetting(settings_constants.GAME.MINIMAP_ALPHA_ENABLED):
            value = int(self.settingsCore.getSetting(settings_constants.GAME.MINIMAP_ALPHA))
        else:
            value = 0.0
        self._parentObj.as_setAlphaS(1 - value / 100.0)


class TeamsOrControlsPointsPlugin(common.EntriesPlugin):
    __slots__ = ('__personalTeam', '__entries', '__markerIDs')

    def __init__(self, parentObj):
        super(TeamsOrControlsPointsPlugin, self).__init__(parentObj)
        self.__personalTeam = 0
        self.__entries = []
        self.__markerIDs = {}

    def start(self):
        super(TeamsOrControlsPointsPlugin, self).start()
        g_playerEvents.onTeamChanged += self.__onTeamChanged
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived += self.__onActionAddedToMarkerReceived
            ctrl.onReplyFeedbackReceived += self.__onReplyFeedbackReceived
            ctrl.onRemoveCommandReceived += self.__onRemoveCommandReceived
        self.restart()
        return

    def stop(self):
        g_playerEvents.onTeamChanged -= self.__onTeamChanged
        super(TeamsOrControlsPointsPlugin, self).stop()
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onActionAddedToMarkerReceived -= self.__onActionAddedToMarkerReceived
            ctrl.onReplyFeedbackReceived -= self.__onReplyFeedbackReceived
            ctrl.onRemoveCommandReceived -= self.__onRemoveCommandReceived
        return

    def restart(self):
        for x in self.__entries:
            self._delEntry(x)

        self.__entries = []
        self.__personalTeam = self._arenaDP.getNumberOfTeam()
        self.__addTeamSpawnPoints()
        self.__addTeamBasePositions()
        self.__addControlPoints()

    def __onActionAddedToMarkerReceived(self, senderID, commandID, markerType, objectID):
        if _ACTIONS.battleChatCommandFromActionID(commandID).name not in BASE_CMD_NAMES:
            return
        if objectID not in self.__markerIDs:
            return
        model = self.__markerIDs[objectID]
        if model:
            if _ACTIONS.battleChatCommandFromActionID(commandID).name in [BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE, BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE]:
                self.__onReplyFeedbackReceived(objectID, senderID, MarkerType.BASE_MARKER_TYPE, 0, 1)
            else:
                self._invoke(model.getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_ATTACK)

    def __onReplyFeedbackReceived--- This code section failed: ---

 225       0	LOAD_FAST         'markerType'
           3	LOAD_GLOBAL       'MarkerType'
           6	LOAD_ATTR         'BASE_MARKER_TYPE'
           9	COMPARE_OP        '!='
          12	POP_JUMP_IF_FALSE '19'

 226      15	LOAD_CONST        ''
          18	RETURN_END_IF     ''

 228      19	LOAD_FAST         'newReplyCount'
          22	LOAD_FAST         'oldReplyCount'
          25	COMPARE_OP        '>'
          28	STORE_FAST        'newReply'

 229      31	LOAD_FAST         'ucmdID'
          34	LOAD_FAST         'self'
          37	LOAD_ATTR         '__markerIDs'
          40	COMPARE_OP        'in'
          43	POP_JUMP_IF_FALSE '152'
          46	LOAD_FAST         'newReply'
        49_0	COME_FROM         '43'
          49	POP_JUMP_IF_FALSE '152'

 230      52	LOAD_FAST         'replierID'
          55	LOAD_GLOBAL       'avatar_getter'
          58	LOAD_ATTR         'getPlayerVehicleID'
          61	CALL_FUNCTION_0   ''
          64	COMPARE_OP        '=='
          67	POP_JUMP_IF_FALSE '111'

 231      70	LOAD_FAST         'self'
          73	LOAD_ATTR         '_invoke'
          76	LOAD_FAST         'self'
          79	LOAD_ATTR         '__markerIDs'
          82	LOAD_FAST         'ucmdID'
          85	BINARY_SUBSCR     ''
          86	LOAD_ATTR         'getID'
          89	CALL_FUNCTION_0   ''
          92	LOAD_GLOBAL       'BATTLE_MINIMAP_CONSTS'
          95	LOAD_ATTR         'SET_STATE'

 232      98	LOAD_GLOBAL       'BATTLE_MINIMAP_CONSTS'
         101	LOAD_ATTR         'STATE_REPLY'
         104	CALL_FUNCTION_3   ''
         107	POP_TOP           ''
         108	JUMP_ABSOLUTE     '152'

 234     111	LOAD_FAST         'self'
         114	LOAD_ATTR         '_invoke'
         117	LOAD_FAST         'self'
         120	LOAD_ATTR         '__markerIDs'
         123	LOAD_FAST         'ucmdID'
         126	BINARY_SUBSCR     ''
         127	LOAD_ATTR         'getID'
         130	CALL_FUNCTION_0   ''
         133	LOAD_GLOBAL       'BATTLE_MINIMAP_CONSTS'
         136	LOAD_ATTR         'SET_STATE'

 235     139	LOAD_GLOBAL       'BATTLE_MINIMAP_CONSTS'
         142	LOAD_ATTR         'STATE_IDLE'
         145	CALL_FUNCTION_3   ''
         148	POP_TOP           ''
         149	JUMP_FORWARD      '152'
       152_0	COME_FROM         '149'

 237     152	LOAD_FAST         'ucmdID'
         155	LOAD_FAST         'self'
         158	LOAD_ATTR         '__markerIDs'
         161	COMPARE_OP        'in'
         164	POP_JUMP_IF_FALSE '253'

 238     167	LOAD_FAST         'newReplyCount'
         170	LOAD_FAST         'oldReplyCount'
         173	COMPARE_OP        '<'
         176	POP_JUMP_IF_FALSE '197'
         179	LOAD_FAST         'replierID'
         182	LOAD_GLOBAL       'avatar_getter'
         185	LOAD_ATTR         'getPlayerVehicleID'
         188	CALL_FUNCTION_0   ''
         191	COMPARE_OP        '=='
       194_0	COME_FROM         '176'
         194	POP_JUMP_IF_TRUE  '209'
         197	LOAD_FAST         'newReplyCount'
         200	LOAD_CONST        0
         203	COMPARE_OP        '<='
       206_0	COME_FROM         '164'
       206_1	COME_FROM         '194'
         206	POP_JUMP_IF_FALSE '253'

 239     209	LOAD_FAST         'self'
         212	LOAD_ATTR         '_invoke'
         215	LOAD_FAST         'self'
         218	LOAD_ATTR         '__markerIDs'
         221	LOAD_FAST         'ucmdID'
         224	BINARY_SUBSCR     ''
         225	LOAD_ATTR         'getID'
         228	CALL_FUNCTION_0   ''
         231	LOAD_GLOBAL       'BATTLE_MINIMAP_CONSTS'
         234	LOAD_ATTR         'SET_STATE'

 240     237	LOAD_GLOBAL       'BATTLE_MINIMAP_CONSTS'
         240	LOAD_ATTR         'STATE_IDLE'
         243	CALL_FUNCTION_3   ''
         246	POP_TOP           ''
         247	JUMP_ABSOLUTE     '253'
         250	JUMP_FORWARD      '253'
       253_0	COME_FROM         '250'

Syntax error at or near 'JUMP_FORWARD' token at offset 250

    def __onRemoveCommandReceived(self, removeID, markerType):
        if not self.__markerIDs or markerType != MarkerType.BASE_MARKER_TYPE:
            return
        if removeID in self.__markerIDs:
            self._invoke(self.__markerIDs[removeID].getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_DEFAULT)
            return
        _logger.error(str(removeID) + ' not found in markerIDs')

    def __onTeamChanged(self, teamID):
        self.restart()

    def __addBaseEntry(self, symbol, position, uid):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        model = self._addEntryEx(uid, symbol, _C_NAME.TEAM_POINTS, matrix=matrix, active=True)
        if model:
            self.__markerIDs[uid] = model
            _, number = getBaseTeamAndIDFromUniqueID(uid)
            self._invoke(model.getID(), BATTLE_MINIMAP_CONSTS.SET_POINT_NUMBER, number)
            self._invoke(model.getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_DEFAULT)

    def __addPointEntry(self, symbol, position, number):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        entryID = self._addEntry(symbol, _C_NAME.TEAM_POINTS, matrix=matrix, active=True)
        if entryID:
            self._invoke(entryID, BATTLE_MINIMAP_CONSTS.SET_POINT_NUMBER, number)
            self.__entries.append(entryID)

    def __addTeamSpawnPoints(self):
        points = self._arenaVisitor.getTeamSpawnPointsIterator(self.__personalTeam)
        for team, position, number in points:
            if team == self.__personalTeam:
                symbol = _S_NAME.ALLY_TEAM_SPAWN
            else:
                symbol = _S_NAME.ENEMY_TEAM_SPAWN
            self.__addPointEntry(symbol, position, number)

    def __addTeamBasePositions(self):
        positions = self._arenaVisitor.type.getTeamBasePositionsIterator()
        for team, position, number in positions:
            if team == self.__personalTeam:
                symbol = _S_NAME.ALLY_TEAM_BASE
            else:
                symbol = _S_NAME.ENEMY_TEAM_BASE
            uid = getUniqueTeamOrControlPointID(team, number)
            self.__addBaseEntry(symbol, position, uid)

    def __addControlPoints(self):
        points = self._arenaVisitor.type.getControlPointsIterator()
        for position, number in points:
            uid = getUniqueTeamOrControlPointID(0, number)
            self.__addBaseEntry(_S_NAME.CONTROL_POINT, position, uid)


class ClassicMinimapPingPlugin(plugins.MinimapPingPlugin):

    def _getClickPosition(self, x, y):
        return minimap_utils.makePointMatrixByLocal(x, y, *self._boundingBox).translation

    def _getIdByBaseNumber(self, team, number):
        return getUniqueTeamOrControlPointID(team, number)

    def _processCommandByPosition(self, commands, locationCommand, position):
        bases = self.__getNearestBaseForPosition(position, _BASE_PING_RANGE)
        if bases is not None:
            self._make3DPingBases(commands, bases)
            return
        else:
            locationID = self._getNearestLocationIDForPosition(position, _LOCATION_PING_RANGE)
            if locationID is not None:
                self._replyPing3DMarker(commands, locationID)
                return
            commands.sendAttentionToPosition3D(position, locationCommand)
            return

    def __getNearestBaseForPosition(self, inPosition, range_):
        positions = self._arenaVisitor.type.getTeamBasePositionsIterator()
        minVal = None
        for team, position, number in positions:
            if minVal is None:
                minVal = (team, position, number)
                continue
            if Math.Vector3(position).flatDistTo(inPosition) < Math.Vector3(minVal[1]).flatDistTo(inPosition):
                minVal = (team, position, number)

        for posControl, number in self._arenaVisitor.type.getControlPointsIterator():
            if minVal is None:
                minVal = (0, posControl, number)
                continue
            if Math.Vector3(posControl).flatDistTo(inPosition) < Math.Vector3(minVal[1]).flatDistTo(inPosition):
                minVal = (0, posControl, number)

        if minVal is None:
            return
        else:
            return minVal if Math.Vector3(minVal[1]).flatDistTo(inPosition) <= range_ else None


class ClassicTeleportPlugin(ClassicMinimapPingPlugin):

    def onMinimapClicked(self, x, y, buttonIdx):
        if buttonIdx != _EMinimapMouseKey.KEY_MBL.value:
            return
        else:
            player = BigWorld.player()
            if player is not None and player.isTeleport:
                position = self._getClickPosition(x, y)
                result = BigWorld.collide(player.spaceID, (position.x, 1000.0, position.z), (position.x, -1000.0, position.z))
                player.base.vehicle_teleport((position[0], result[0][1], position[2]), 0)
            return