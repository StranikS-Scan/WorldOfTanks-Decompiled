# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/classic/minimap.py
import BigWorld
import Keys
import Math
import CommandMapping
from account_helpers import AccountSettings
from account_helpers.settings_core import g_settingsCore, settings_constants
from gui import GUI_SETTINGS, g_repeatKeyHandlers
from gui.Scaleform.daapi.view.battle.shared.minimap import common
from gui.Scaleform.daapi.view.battle.shared.minimap import component
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.battle_control import minimap_utils, avatar_getter, g_sessionProvider
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from messenger import MessengerEntry
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME

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
        value = int(g_settingsCore.getSetting(settings_constants.GAME.MINIMAP_ALPHA))
        if value:
            self._parentObj.as_setAlphaS(1 - value / 100.0)

    def updateSettings(self, diff):
        if settings_constants.GAME.MINIMAP_ALPHA in diff:
            value = int(diff[settings_constants.GAME.MINIMAP_ALPHA])
            self._parentObj.as_setAlphaS(1 - value / 100.0)

    def _changeSizeSettings(self, newSizeSettings):
        """
        we can have different settings for minimap size
        :param newSizeSettings: new name of settings
        :return: current name of settings
        """
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
        if newIndex != self.__sizeIndex:
            self.__sizeIndex = newIndex
            self._parentObj.as_setSizeS(newIndex)
        self.__saveSettings()

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


class TeamsOrControlsPointsPlugin(common.SimplePlugin):
    __slots__ = ('__personalTeam',)

    def __init__(self, parentObj):
        super(TeamsOrControlsPointsPlugin, self).__init__(parentObj)
        self.__personalTeam = 0

    def start(self):
        super(TeamsOrControlsPointsPlugin, self).start()
        self.__personalTeam = self._arenaDP.getNumberOfTeam()
        self.__addTeamSpawnPoints()
        self.__addTeamBasePositions()
        self.__addControlPoints()

    def __addPointEntry(self, symbol, position, number):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        entryID = self._addEntry(symbol, _C_NAME.TEAM_POINTS, matrix=matrix, active=True)
        if entryID:
            self._invoke(entryID, 'setPointNumber', number)

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

    def setAttentionToCell(self, x, y, isRightClick):
        if isRightClick:
            handler = avatar_getter.getInputHandler()
            if handler is not None:
                matrix = minimap_utils.makePointMatrixByLocal(x, y, *self._boundingBox)
                handler.onMinimapClicked(matrix.translation)
        else:
            commands = g_sessionProvider.shared.chatCommands
            if commands is not None:
                commands.sendAttentionToCell(minimap_utils.makeCellIndex(x, y))
        return

    def _doAttention(self, index, duration):
        matrix = minimap_utils.makePointMatrixByCellIndex(index, *self._boundingBox)
        model = self._addEntryEx(index, _S_NAME.MARK_CELL, _C_NAME.PERSONAL, matrix=matrix, active=True)
        if model is not None:
            self._invoke(model.getID(), 'playAnimation')
            self._setCallback(index, duration)
            self._playSound2D(settings.MINIMAP_ATTENTION_SOUND_ID)
        return
