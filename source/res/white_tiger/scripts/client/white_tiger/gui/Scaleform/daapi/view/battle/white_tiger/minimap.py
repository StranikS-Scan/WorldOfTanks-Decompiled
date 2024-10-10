# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/minimap.py
import typing
from Math import Matrix
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent
from gui.Scaleform.daapi.view.battle.shared.minimap.common import EntriesPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import ArenaVehiclesPlugin, AreaMarkerEntriesPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import CONTAINER_NAME
from gui.Scaleform.daapi.view.battle.classic.minimap import GlobalSettingsPlugin
from chat_commands_consts import INVALID_MARKER_ID
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.teleport_spawn_ctrl import TeleportSpawnController

class WhiteTigerSettingsPlugin(GlobalSettingsPlugin):

    def start(self):
        super(WhiteTigerSettingsPlugin, self).start()
        g_eventBus.addListener(events.GameEvent.SHOW_SPAWN_POINTS, self.__onShowSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(events.GameEvent.HIDE_SPAWN_POINTS, self.__onHideSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)

    def stop(self):
        g_eventBus.removeListener(events.GameEvent.HIDE_SPAWN_POINTS, self.__onHideSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.removeListener(events.GameEvent.SHOW_SPAWN_POINTS, self.__onShowSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)
        super(WhiteTigerSettingsPlugin, self).stop()

    def __onShowSpawnPoints(self, _):
        if self._parentObj is not None:
            self._parentObj.as_setVisibleS(True)
        return

    def __onHideSpawnPoints(self, _):
        if self._parentObj is not None:
            self._parentObj.as_setVisibleS(self._isVisible)
        return


class WhiteTigerMinimapComponent(ClassicMinimapComponent):

    def __init__(self):
        super(WhiteTigerMinimapComponent, self).__init__()
        self.__isActiveSpawnPoints = False

    def _setupPlugins(self, arenaVisitor):
        setup = super(WhiteTigerMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['spawn_points'] = SpawnPointsPlugin
        setup['vehicles'] = WhiteTigerArenaVehiclesPlugin
        setup['settings'] = WhiteTigerSettingsPlugin
        setup['area_markers'] = WhiteTigerBaseAreaMarkerEntriesPlugin
        return setup

    def _populate(self):
        super(WhiteTigerMinimapComponent, self)._populate()
        g_eventBus.addListener(events.GameEvent.SHOW_SPAWN_POINTS, self.__onShowSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(events.GameEvent.HIDE_SPAWN_POINTS, self.__onHideSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)

    def _dispose(self):
        g_eventBus.removeListener(events.GameEvent.HIDE_SPAWN_POINTS, self.__onHideSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.removeListener(events.GameEvent.SHOW_SPAWN_POINTS, self.__onShowSpawnPoints, EVENT_BUS_SCOPE.GLOBAL)
        super(WhiteTigerMinimapComponent, self)._dispose()

    def isModalViewShown(self):
        return True if self.__isActiveSpawnPoints else super(WhiteTigerMinimapComponent, self).isModalViewShown()

    def __onShowSpawnPoints(self, _):
        self.__isActiveSpawnPoints = True
        mpp = self.getPlugin('pinging')
        if mpp is not None:
            mpp.hideHintPanel(instantHide=True)
        avp = self.getPlugin('vehicles')
        avp.hideMinimapHP()
        return

    def __onHideSpawnPoints(self, _):
        self.__isActiveSpawnPoints = False


class SpawnPointsPlugin(EntriesPlugin):
    __slots__ = ('_points',)
    _SPAWN_POINT_ENTRY = 'WTDeploymentPointMinimapEntryUI'

    def __init__(self, parent, clazz=None):
        super(SpawnPointsPlugin, self).__init__(parent, clazz)
        self._points = {}

    def start(self):
        super(SpawnPointsPlugin, self).start()
        spawnCtrl = self._spawnCtrl
        if spawnCtrl:
            spawnCtrl.onShowSpawnPoints += self._onShowSpawnPoints
            spawnCtrl.onCloseSpawnPoints += self._onCloseSpawnPoints
            spawnCtrl.onChooseSpawnPoint += self._onChooseSpawnPoint

    def stop(self):
        spawnCtrl = self._spawnCtrl
        if spawnCtrl:
            spawnCtrl.onShowSpawnPoints -= self._onShowSpawnPoints
            spawnCtrl.onCloseSpawnPoints -= self._onCloseSpawnPoints
            spawnCtrl.onChooseSpawnPoint -= self._onChooseSpawnPoint
        super(SpawnPointsPlugin, self).stop()

    @property
    def _spawnCtrl(self):
        return self.sessionProvider.dynamic.teleport

    def _onShowSpawnPoints(self, points, pointGuid):
        self._removeMarkers()
        self._setPoints(points)
        self._addMarkers()
        self._choosePoint(pointGuid)

    def _onCloseSpawnPoints(self):
        self._removeMarkers()

    def _onChooseSpawnPoint(self, pointGuid):
        self._choosePoint(pointGuid)

    def _setPoints(self, points):
        self._points = {point['guid']:(point['position'][0], 0, point['position'][1]) for point in points}

    def _addMarkers(self):
        for pointGuid, position in self._points.iteritems():
            matrix = Matrix()
            matrix.setTranslate(position)
            self._addEntryEx(pointGuid, self._SPAWN_POINT_ENTRY, CONTAINER_NAME.WT_DEPLOY, matrix, active=True)
            self._invokeEx(pointGuid, 'setId', pointGuid)

    def _removeMarkers(self):
        for pointGuid in self._points:
            self._delEntryEx(pointGuid)

        self._points = {}

    def _choosePoint(self, chosenGuid):
        for pointGuid in self._points:
            self._invokeEx(pointGuid, 'setIsSelected', pointGuid == chosenGuid)


class WhiteTigerArenaVehiclesPlugin(ArenaVehiclesPlugin):

    def _setVehicleInfo(self, vehicleID, entry, vInfo, guiProps, isSpotted=False):
        vehicleType = vInfo.vehicleType
        classTag = vehicleType.classTag
        name = vehicleType.shortNameWithPrefix
        if 'event_boss' in vehicleType.tags:
            classTag = 'boss'
        if classTag is not None:
            entry.setVehicleInfo(not guiProps.isFriend, guiProps.name(), classTag, vInfo.isAlive())
            animation = self._ArenaVehiclesPlugin__getSpottedAnimation(entry, isSpotted)
            if animation:
                self._ArenaVehiclesPlugin__playSpottedSound(entry)
            self._invoke(entry.getID(), 'setVehicleInfo', vehicleID, classTag, name, guiProps.name(), animation)
        return


class WhiteTigerBaseAreaMarkerEntriesPlugin(AreaMarkerEntriesPlugin):
    __slots__ = ('__entityMap',)

    def __init__(self, parentObj):
        super(WhiteTigerBaseAreaMarkerEntriesPlugin, self).__init__(parentObj)
        self.__entityMap = {}

    def createMarker(self, uniqueID, symbol, container, matrix, active):
        model = self._addEntryEx(uniqueID, symbol, container, matrix=matrix, active=active)
        return True if model is not None else False

    def deleteMarker(self, uniqueID):
        self._delEntryEx(uniqueID)

    def setMatrix(self, uniqueID, matrix):
        self._setMatrixEx(uniqueID, matrix)

    def update(self, *args, **kwargs):
        super(WhiteTigerBaseAreaMarkerEntriesPlugin, self).update()

    def invoke(self, uniqueID, name, *args):
        self._invokeEx(uniqueID, name, *args)

    def setActive(self, uniqueID, isActive):
        self._setActiveEx(uniqueID, isActive)

    def mapCustomEntityID(self, uniqueID, entityID):
        self.__entityMap[uniqueID] = entityID

    def deleteCustomEntityID(self, uniqueID):
        if uniqueID in self.__entityMap:
            self.__entityMap.pop(uniqueID)

    def getMarkerIdFormEntityID(self, entityID):
        for entityIDEntry in self.__entityMap:
            if self.__entityMap[entityIDEntry] == entityID:
                return entityIDEntry

        return INVALID_MARKER_ID
