# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/festival_race/minimap.py
import BigWorld
import Keys
import CommandMapping
from helpers import isPlayerAvatar, dependency
from account_helpers import AccountSettings
from account_helpers.settings_core import settings_constants
from gui import GUI_SETTINGS, g_repeatKeyHandlers
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.meta.FestivalRaceMinimapMeta import FestivalRaceMinimapMeta
from gui.Scaleform.daapi.view.battle.shared.minimap import plugins, common, settings
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from messenger import MessengerEntry
from skeletons.gui.battle_session import IBattleSessionProvider
from debug_utils import LOG_DEBUG

class FestivalRaceSettingsPlugin(common.SimplePlugin):
    __slots__ = ('__currentSizeSettings', '__isVisible', '__sizeIndex')

    def __init__(self, parentObj):
        super(FestivalRaceSettingsPlugin, self).__init__(parentObj)
        self.__currentSizeSettings = 'festivalRaceMinimapSize'
        self.__isVisible = True
        self.__sizeIndex = 0

    def start(self):
        super(FestivalRaceSettingsPlugin, self).start()
        if GUI_SETTINGS.minimapSize:
            g_eventBus.addListener(events.GameEvent.MINIMAP_CMD, self.__handleMinimapCmd, scope=EVENT_BUS_SCOPE.BATTLE)
            g_repeatKeyHandlers.add(self.__handleRepeatKeyEvent)

    def stop(self):
        if GUI_SETTINGS.minimapSize:
            g_eventBus.removeListener(events.GameEvent.MINIMAP_CMD, self.__handleMinimapCmd, scope=EVENT_BUS_SCOPE.BATTLE)
            g_repeatKeyHandlers.discard(self.__handleRepeatKeyEvent)
        super(FestivalRaceSettingsPlugin, self).stop()

    def setSettings(self):
        newSize = settings.clampRaceMinimapSizeIndex(AccountSettings.getSettings(self.__currentSizeSettings))
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

    @staticmethod
    def _clampMinimapSizeIndex(szIndex):
        return settings.clampRaceMinimapSizeIndex(szIndex)

    def _toogleVisible(self):
        self.__isVisible = not self.__isVisible
        self._parentObj.as_setVisibleS(self.__isVisible)

    def __saveSettings(self):
        AccountSettings.setSettings(self.__currentSizeSettings, self.__sizeIndex)

    def __setSizeByStep(self, step):
        newIndex = self._clampMinimapSizeIndex(self.__sizeIndex + step)
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


class FestivalRaceMinimapComponent(FestivalRaceMinimapMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _populate(self):
        super(FestivalRaceMinimapComponent, self)._populate()
        self.__vehID = None
        self._arenaDP = self.sessionProvider.getArenaDP()
        self.__addListeners()
        self.__initRacePosition()
        return

    def _dispose(self):
        self.__removeListeners()
        self._arenaDP = None
        super(FestivalRaceMinimapComponent, self)._dispose()
        return

    def _setupPlugins(self, arenaVisitor):
        setup = super(FestivalRaceMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['settings'] = FestivalRaceSettingsPlugin
        setup['vehicles'] = plugins.RaceArenaVehiclesPlugin
        setup['personal'] = plugins.RacePersonalEntriesPlugin
        setup.pop('points')
        return setup

    def __addListeners(self):
        player = BigWorld.player()
        if isPlayerAvatar():
            player.onNewRacePosition += self.__onNewRacePosition
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated

    def __onNewRacePosition(self, newPosition):
        playersCount = len(list(self._arenaDP.getVehiclesInfoIterator()))
        self.as_setPositionS(newPosition, playersCount)

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.SWITCHING:
            if self.__vehID is not None:
                player = BigWorld.player()
                if isPlayerAvatar() and player.isEnabledRace:
                    player.onNewRacePosition -= self.__onNewRacePosition
                ctrl = self.sessionProvider.dynamic.eventRacePosition
                if ctrl is not None:
                    ctrl.onRacePositionsUpdate += self.__updatePositions
            self.__vehID = value
            if BigWorld.player().arena.arenaInfo is not None:
                raceList = BigWorld.player().arena.arenaInfo.raceList
                self.__updatePositions(raceList)
        return

    def __updatePositions(self, raceList):
        position = self.__getVehiclePositionInList(self.__vehID, raceList)
        self.__onNewRacePosition(position)

    def __initRacePosition(self):
        if BigWorld.player().arena.arenaInfo is not None:
            vehID = self._arenaDP.getPlayerVehicleID()
            raceList = BigWorld.player().arena.arenaInfo.raceList
            playerPosition = self.__getVehiclePositionInList(vehID, raceList)
            if playerPosition is not None:
                self.__onNewRacePosition(playerPosition)
        return

    def __getVehiclePositionInList(self, vehID, raceList):
        return next((pos for pos, vehicleID in raceList if vehicleID == vehID), None)

    def __removeListeners(self):
        player = BigWorld.player()
        if isPlayerAvatar() and player.isEnabledRace:
            player.onNewRacePosition -= self.__onNewRacePosition
        ctrl = self.sessionProvider.dynamic.eventRacePosition
        if ctrl is not None:
            ctrl.onRacePositionsUpdate -= self.__updatePositions
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        return
