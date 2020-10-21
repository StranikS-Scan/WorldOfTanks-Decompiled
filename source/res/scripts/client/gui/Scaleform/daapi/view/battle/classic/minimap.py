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
_CLASSIC_MINIMAP_DIMENSIONS = 10

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

    def hasMinimapGrid(self):
        return True

    def getMinimapDimensions(self):
        return _CLASSIC_MINIMAP_DIMENSIONS


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
    __slots__ = ('__personalTeam', '__entries', '__markerIDs', '__hasActiveCommit')

    def __init__(self, parentObj):
        super(TeamsOrControlsPointsPlugin, self).__init__(parentObj)
        self.__personalTeam = 0
        self.__entries = []
        self.__markerIDs = {}
        self.__hasActiveCommit = False

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
        elif objectID not in self.__markerIDs:
            return
        else:
            model = self.__markerIDs[objectID]
            if model is not None:
                if _ACTIONS.battleChatCommandFromActionID(commandID).name in [BATTLE_CHAT_COMMAND_NAMES.ATTACKING_BASE, BATTLE_CHAT_COMMAND_NAMES.DEFENDING_BASE]:
                    self.__onReplyFeedbackReceived(objectID, senderID, MarkerType.BASE_MARKER_TYPE, 0, 1)
                else:
                    self._invoke(model.getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_ATTACK)
            return

    def __onReplyFeedbackReceived--- This code section failed: ---

 234       0	LOAD_FAST         'markerType'
           3	LOAD_GLOBAL       'MarkerType'
           6	LOAD_ATTR         'BASE_MARKER_TYPE'
           9	COMPARE_OP        '!='
          12	POP_JUMP_IF_FALSE '19'

 235      15	LOAD_CONST        ''
          18	RETURN_END_IF     ''

 237      19	LOAD_FAST         'newReplyCount'
          22	LOAD_FAST         'oldReplyCount'
          25	COMPARE_OP        '>'
          28	STORE_FAST        'newReply'

 238      31	LOAD_FAST         'replierID'
          34	LOAD_GLOBAL       'avatar_getter'
          37	LOAD_ATTR         'getPlayerVehicleID'
          40	CALL_FUNCTION_0   ''
          43	COMPARE_OP        '=='
          46	STORE_FAST        'playerHasReply'

 239      49	LOAD_FAST         'ucmdID'
          52	LOAD_FAST         'self'
          55	LOAD_ATTR         '__markerIDs'
          58	COMPARE_OP        'in'
          61	POP_JUMP_IF_FALSE '179'
          64	LOAD_FAST         'newReply'
        67_0	COME_FROM         '61'
          67	POP_JUMP_IF_FALSE '179'

 240      70	LOAD_FAST         'playerHasReply'
          73	POP_JUMP_IF_FALSE '126'

 241      76	LOAD_FAST         'self'
          79	LOAD_ATTR         '_invoke'
          82	LOAD_FAST         'self'
          85	LOAD_ATTR         '__markerIDs'
          88	LOAD_FAST         'ucmdID'
          91	BINARY_SUBSCR     ''
          92	LOAD_ATTR         'getID'
          95	CALL_FUNCTION_0   ''
          98	LOAD_GLOBAL       'BATTLE_MINIMAP_CONSTS'
         101	LOAD_ATTR         'SET_STATE'

 242     104	LOAD_GLOBAL       'BATTLE_MINIMAP_CONSTS'
         107	LOAD_ATTR         'STATE_REPLY'
         110	CALL_FUNCTION_3   ''
         113	POP_TOP           ''

 243     114	LOAD_GLOBAL       'True'
         117	LOAD_FAST         'self'
         120	STORE_ATTR        '__hasActiveCommit'
         123	JUMP_ABSOLUTE     '179'

 244     126	LOAD_FAST         'self'
         129	LOAD_ATTR         '__hasActiveCommit'
         132	POP_JUMP_IF_TRUE  '179'

 245     135	LOAD_FAST         'self'
         138	LOAD_ATTR         '_invoke'
         141	LOAD_FAST         'self'
         144	LOAD_ATTR         '__markerIDs'
         147	LOAD_FAST         'ucmdID'
         150	BINARY_SUBSCR     ''
         151	LOAD_ATTR         'getID'
         154	CALL_FUNCTION_0   ''
         157	LOAD_GLOBAL       'BATTLE_MINIMAP_CONSTS'
         160	LOAD_ATTR         'SET_STATE'

 246     163	LOAD_GLOBAL       'BATTLE_MINIMAP_CONSTS'
         166	LOAD_ATTR         'STATE_IDLE'
         169	CALL_FUNCTION_3   ''
         172	POP_TOP           ''
         173	JUMP_ABSOLUTE     '179'
         176	JUMP_FORWARD      '179'
       179_0	COME_FROM         '176'

 248     179	LOAD_FAST         'ucmdID'
         182	LOAD_FAST         'self'
         185	LOAD_ATTR         '__markerIDs'
         188	COMPARE_OP        'in'
         191	POP_JUMP_IF_FALSE '286'

 249     194	LOAD_FAST         'newReplyCount'
         197	LOAD_FAST         'oldReplyCount'
         200	COMPARE_OP        '<'
         203	POP_JUMP_IF_FALSE '212'
         206	LOAD_FAST         'playerHasReply'
       209_0	COME_FROM         '203'
         209	POP_JUMP_IF_TRUE  '224'
         212	LOAD_FAST         'newReplyCount'
         215	LOAD_CONST        0
         218	COMPARE_OP        '<='
       221_0	COME_FROM         '191'
       221_1	COME_FROM         '209'
         221	POP_JUMP_IF_FALSE '286'

 250     224	LOAD_FAST         'self'
         227	LOAD_ATTR         '_invoke'
         230	LOAD_FAST         'self'
         233	LOAD_ATTR         '__markerIDs'
         236	LOAD_FAST         'ucmdID'
         239	BINARY_SUBSCR     ''
         240	LOAD_ATTR         'getID'
         243	CALL_FUNCTION_0   ''
         246	LOAD_GLOBAL       'BATTLE_MINIMAP_CONSTS'
         249	LOAD_ATTR         'SET_STATE'

 251     252	LOAD_GLOBAL       'BATTLE_MINIMAP_CONSTS'
         255	LOAD_ATTR         'STATE_IDLE'
         258	CALL_FUNCTION_3   ''
         261	POP_TOP           ''

 252     262	LOAD_FAST         'playerHasReply'
         265	POP_JUMP_IF_FALSE '283'

 253     268	LOAD_GLOBAL       'False'
         271	LOAD_FAST         'self'
         274	STORE_ATTR        '__hasActiveCommit'
         277	JUMP_ABSOLUTE     '283'
         280	JUMP_ABSOLUTE     '286'
         283	JUMP_FORWARD      '286'
       286_0	COME_FROM         '283'

Syntax error at or near 'JUMP_FORWARD' token at offset 283

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
        if model is not None:
            self.__markerIDs[uid] = model
            _, number = getBaseTeamAndIDFromUniqueID(uid)
            self._invoke(model.getID(), BATTLE_MINIMAP_CONSTS.SET_POINT_NUMBER, number)
            self._invoke(model.getID(), BATTLE_MINIMAP_CONSTS.SET_STATE, BATTLE_MINIMAP_CONSTS.STATE_DEFAULT)
        return

    def __addPointEntry(self, symbol, position, number):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        entryID = self._addEntry(symbol, _C_NAME.TEAM_POINTS, matrix=matrix, active=True)
        if entryID:
            self._invoke(entryID, BATTLE_MINIMAP_CONSTS.SET_POINT_NUMBER, number)
            self.__entries.append(entryID)
            return entryID

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

    def _processCommandByPosition(self, commands, locationCommand, position, minimapScaleIndex):
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

    def onMinimapClicked(self, x, y, buttonIdx, minimapScaleIndex):
        if buttonIdx != _EMinimapMouseKey.KEY_MBL.value:
            return
        else:
            player = BigWorld.player()
            if player is not None and player.isTeleport:
                position = self._getClickPosition(x, y)
                result = BigWorld.collide(player.spaceID, (position.x, 1000.0, position.z), (position.x, -1000.0, position.z))
                player.base.vehicle_teleport((position[0], result[0][1], position[2]), 0)
            return