# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/minimap.py
import logging
import CommandMapping
from gui.Scaleform.daapi.view.battle.shared.minimap import common
from gui.Scaleform.daapi.view.battle.shared.minimap import component
from gui.Scaleform.daapi.view.battle.shared.minimap import plugins
from gui import GUI_SETTINGS
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
_logger = logging.getLogger(__name__)

class EventMinimapSettingsPlugin(common.SimplePlugin):

    def start(self):
        super(EventMinimapSettingsPlugin, self).start()
        if GUI_SETTINGS.minimapSize:
            g_eventBus.addListener(events.GameEvent.EVENT_MINIMAP_CMD, self.__handleMinimapCmd, scope=EVENT_BUS_SCOPE.BATTLE)
        self._parentObj.as_setVisibleS(False)
        maximumMinimapSize = 5
        self._parentObj.as_setSizeS(maximumMinimapSize)

    def stop(self):
        if GUI_SETTINGS.minimapSize:
            g_eventBus.removeListener(events.GameEvent.EVENT_MINIMAP_CMD, self.__handleMinimapCmd, scope=EVENT_BUS_SCOPE.BATTLE)
        super(EventMinimapSettingsPlugin, self).stop()

    def __handleMinimapCmd(self, event):
        isDown = event.ctx['isDown']
        self.__handleKey(event.ctx['key'], isDown)

    def __handleKey(self, key, isDown):
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFiredList((CommandMapping.CMD_MINIMAP_VISIBLE, CommandMapping.CMD_EVENT_MAP_VISIBLE), key):
            self._parentObj.as_setVisibleS(isDown)


class PvePersonalEntriesPlugin(plugins.PersonalEntriesPlugin):

    def _invalidateMarkup(self, forceInvalidate=False):
        super(PvePersonalEntriesPlugin, self)._invalidateMarkup(forceInvalidate)
        self._showCircles(False)
        self._updateDirectionLine(False)


class PveArenaVehiclesPlugin(plugins.ArenaVehiclesPlugin):

    def __init__(self, parent):
        super(PveArenaVehiclesPlugin, self).__init__(parent)
        self.__showDestroyEntries = False

    def _setVehicleInfo(self, vehicleID, entry, vInfo, guiProps, isSpotted=False):
        if guiProps.isFriend:
            super(PveArenaVehiclesPlugin, self)._setVehicleInfo(vehicleID, entry, vInfo, guiProps, False)

    def _onMinimapVehicleAdded(self, vProxy, vInfo, guiProps):
        if guiProps.isFriend:
            super(PveArenaVehiclesPlugin, self)._onMinimapVehicleAdded(vProxy, vInfo, guiProps)

    def setSettings(self):
        pass

    def updateSettings(self, diff):
        pass


class EventMinimapComponent(component.MinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(EventMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['settings'] = EventMinimapSettingsPlugin
        setup['personal'] = PvePersonalEntriesPlugin
        setup['vehicles'] = PveArenaVehiclesPlugin
        return setup
