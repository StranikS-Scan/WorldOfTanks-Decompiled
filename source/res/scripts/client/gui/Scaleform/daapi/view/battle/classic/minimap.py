# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/minimap.py
import BigWorld
import Keys
import Math
import CommandMapping
from account_helpers import AccountSettings
from account_helpers.settings_core import settings_constants
from debug_utils import LOG_DEBUG
from gui import GUI_SETTINGS, g_repeatKeyHandlers
from gui.Scaleform.daapi.view.battle.shared.minimap import common
from gui.Scaleform.daapi.view.battle.shared.minimap import component
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.battle_control import minimap_utils, avatar_getter
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from messenger import MessengerEntry
from skeletons.gui.battle_session import IBattleSessionProvider
from PlayerEvents import g_playerEvents
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME
_MARK_CELL_UNIQUE_ID = 0

class ClassicMinimapComponent(component.MinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(ClassicMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['settings'] = GlobalSettingsPlugin
        setup['points'] = TeamsOrControlsPointsPlugin
        setup['cells'] = MarkCellPlugin
        return setup


class GlobalSettingsPlugin(common.SimplePlugin):
    __slots__ = ('__currentSizeSettings', '__isVisible', '__sizeIndex')

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
        newSize = settings.clampMinimapSizeIndex(AccountSettings.getSettings(self.__currentSizeSettings))
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

    def __saveSettings(self):
        AccountSettings.setSettings(self.__currentSizeSettings, self.__sizeIndex)

    def __setSizeByStep(self, step):
        newIndex = settings.clampMinimapSizeIndex(self.__sizeIndex + step)
        if self.__sizeIndex != newIndex:
            LOG_DEBUG('Try to change size index of minimap by step', newIndex)
            self._parentObj.as_setSizeS(newIndex)

    def __toogleVisible(self):
        self.__isVisible = not self.__isVisible
        self._parentObj.as_setVisibleS(self.__isVisible)

    def __handleKey(self, key):
        if self._parentObj.isModalViewShown():
            return
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFired(CommandMapping.CMD_MINIMAP_SIZE_DOWN, key):
            self.__setSizeByStep(-1)
        elif cmdMap.isFired(CommandMapping.CMD_MINIMAP_SIZE_UP, key):
            self.__setSizeByStep(1)
        elif cmdMap.isFired(CommandMapping.CMD_MINIMAP_VISIBLE, key):
            self.__toogleVisible()

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


class TeamsOrControlsPointsPlugin(common.SimplePlugin):
    __slots__ = ('__personalTeam', '__entries')

    def __init__(self, parentObj):
        super(TeamsOrControlsPointsPlugin, self).__init__(parentObj)
        self.__personalTeam = 0
        self.__entries = []

    def start(self):
        super(TeamsOrControlsPointsPlugin, self).start()
        g_playerEvents.onTeamChanged += self.__onTeamChanged
        self.restart()

    def stop(self):
        g_playerEvents.onTeamChanged -= self.__onTeamChanged
        super(TeamsOrControlsPointsPlugin, self).stop()

    def restart(self):
        for x in self.__entries:
            self._delEntry(x)

        self.__entries = []
        self.__personalTeam = self._arenaDP.getNumberOfTeam()
        self.__addTeamSpawnPoints()
        self.__addTeamBasePositions()
        self.__addControlPoints()

    def __onTeamChanged(self, teamID):
        self.restart()

    def __addPointEntry(self, symbol, position, number):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        entryID = self._addEntry(symbol, _C_NAME.TEAM_POINTS, matrix=matrix, active=True)
        if entryID:
            self._invoke(entryID, 'setPointNumber', number)
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
            self.__addPointEntry(symbol, position, number)

    def __addControlPoints(self):
        points = self._arenaVisitor.type.getControlPointsIterator()
        for position, number in points:
            self.__addPointEntry(_S_NAME.CONTROL_POINT, position, number)


class MarkCellPlugin(common.AttentionToCellPlugin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def setAttentionToCell(self, x, y, isRightClick):
        if isRightClick:
            handler = avatar_getter.getInputHandler()
            if handler is not None:
                matrix = minimap_utils.makePointMatrixByLocal(x, y, *self._boundingBox)
                handler.onMinimapClicked(matrix.translation)
        else:
            commands = self.sessionProvider.shared.chatCommands
            if commands is not None:
                commands.sendAttentionToCell(minimap_utils.makeCellIndex(x, y))
        return

    def _doAttention(self, index, duration):
        matrix = minimap_utils.makePointMatrixByCellIndex(index, *self._boundingBox)
        uniqueID = _MARK_CELL_UNIQUE_ID
        if uniqueID in self._entries:
            model = self._entries[uniqueID]
            self._clearCallback(uniqueID)
            self._setMatrix(model.getID(), matrix)
        else:
            model = self._addEntryEx(uniqueID, _S_NAME.MARK_CELL, _C_NAME.PERSONAL, matrix=matrix, active=True)
        if model is not None:
            self._invoke(model.getID(), 'playAnimation')
            self._setCallback(uniqueID, duration)
            self._playSound2D(settings.MINIMAP_ATTENTION_SOUND_ID)
        return
