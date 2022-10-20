# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/battle/minimap.py
import BigWorld
import Event
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent
from gui.Scaleform.daapi.view.battle.shared.minimap import settings, plugins
from halloween.gui.shared.events import BuffGUIEvent
_S_NAME = settings.ENTRY_SYMBOL_NAME

class HWMinimapComponent(ClassicMinimapComponent):

    def __init__(self):
        super(HWMinimapComponent, self).__init__()
        self.__eManager = Event.EventManager()
        self.onVehicleBuffMarkerUpdated = Event.Event(self.__eManager)
        self.onAvatarBuffMarkerUpdated = Event.Event(self.__eManager)

    def _setupPlugins(self, arenaVisitor):
        setup = super(HWMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['vehicles'] = HWArenaVehiclesPlugin
        setup['personal'] = HWPersonalEntriesPlugin
        return setup

    def _populate(self):
        super(HWMinimapComponent, self)._populate()
        self.addListener(BuffGUIEvent.ON_GLOBAL_APPLY, self.__handleBuffApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(BuffGUIEvent.ON_GLOBAL_UNAPPLY, self.__handleBuffUnApply, scope=EVENT_BUS_SCOPE.BATTLE)

    def _dispose(self):
        self.removeListener(BuffGUIEvent.ON_GLOBAL_APPLY, self.__handleBuffApply, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(BuffGUIEvent.ON_GLOBAL_UNAPPLY, self.__handleBuffUnApply, scope=EVENT_BUS_SCOPE.BATTLE)
        super(HWMinimapComponent, self)._dispose()

    def __handleBuffUnApply(self, event):
        self.__onBuffGUIEvent(event, False)

    def __handleBuffApply(self, event):
        self.__onBuffGUIEvent(event, True)

    def __onBuffGUIEvent(self, event, isApplied):
        eventCtx = event.ctx
        vehicleID = eventCtx['vehicleID']
        buffName = eventCtx['id']
        player = BigWorld.player()
        if player and player.playerVehicleID == vehicleID:
            self.onAvatarBuffMarkerUpdated(buffName, isApplied)
        else:
            self.onVehicleBuffMarkerUpdated(vehicleID, buffName, isApplied)


class HWArenaVehiclesPlugin(plugins.ArenaVehiclesPlugin):
    __slots__ = ('__appliedBuffNames',)

    def __init__(self, parentObj):
        super(HWArenaVehiclesPlugin, self).__init__(parentObj)
        self.__appliedBuffNames = {}

    def start(self):
        super(HWArenaVehiclesPlugin, self).start()
        self._parentObj.onVehicleBuffMarkerUpdated += self.__onVehicleBuffMarkerUpdated

    def stop(self):
        self._parentObj.onVehicleBuffMarkerUpdated -= self.__onVehicleBuffMarkerUpdated
        super(HWArenaVehiclesPlugin, self).stop()

    def _addEntryEx(self, uniqueID, symbol, container, matrix=None, active=False, transformProps=settings.TRANSFORM_FLAG.DEFAULT):
        if symbol == _S_NAME.VEHICLE:
            symbol = 'HWVehicleMinimapMarker'
        return super(HWArenaVehiclesPlugin, self)._addEntryEx(uniqueID, symbol, container, matrix=matrix, active=active, transformProps=transformProps)

    def __onVehicleBuffMarkerUpdated(self, vehicleID, buffName, isVisible):
        entry = self._entries.get(vehicleID, None)
        if not entry:
            return
        else:
            if not isVisible:
                activeBuffName = self.__appliedBuffNames.get(vehicleID, None)
                if activeBuffName != buffName:
                    return
            else:
                self.__appliedBuffNames[vehicleID] = buffName
            self._invoke(entry.getID(), 'setBuff', isVisible)
            return


class HWPersonalEntriesPlugin(plugins.PersonalEntriesPlugin):
    __slots__ = ('__entryID', '__appliedBuffName')

    def __init__(self, parentObj):
        super(HWPersonalEntriesPlugin, self).__init__(parentObj)
        self.__entryID = None
        self.__appliedBuffName = None
        return

    def start(self):
        super(HWPersonalEntriesPlugin, self).start()
        self._parentObj.onAvatarBuffMarkerUpdated += self.__onAvatarBuffMarkerUpdated

    def stop(self):
        self._parentObj.onAvatarBuffMarkerUpdated -= self.__onAvatarBuffMarkerUpdated
        super(HWPersonalEntriesPlugin, self).stop()

    def _addEntry(self, symbol, container, matrix=None, active=False, transformProps=settings.TRANSFORM_FLAG.DEFAULT):
        needsReplaceSymbol = symbol == _S_NAME.VIEW_POINT
        if needsReplaceSymbol:
            symbol = 'HWViewPointMinimapEntryUI'
        entryID = super(HWPersonalEntriesPlugin, self)._addEntry(symbol, container, matrix=matrix, active=active, transformProps=transformProps)
        if needsReplaceSymbol:
            self.__entryID = entryID
        return entryID

    def __onAvatarBuffMarkerUpdated(self, buffName, isApplied):
        if self.__entryID is None:
            return
        else:
            if not isApplied:
                if self.__appliedBuffName != buffName:
                    return
            else:
                self.__appliedBuffName = buffName
            self._invoke(self.__entryID, 'setBuff', isApplied)
            return
