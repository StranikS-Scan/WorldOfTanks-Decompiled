# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/minimap.py
from functools import partial
import BigWorld
import GUI
import Math
from AvatarInputHandler.aih_constants import CTRL_MODE_NAME
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent
from gui.Scaleform.daapi.view.battle.classic.minimap import GlobalSettingsPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import PersonalEntriesPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.common import EntriesPlugin
from gui.battle_control import minimap_utils
from gui.Scaleform.daapi.view.battle.shared.minimap.entries import VehicleEntry
from gui.Scaleform.genConsts.APP_CONTAINERS_NAMES import APP_CONTAINERS_NAMES
from gui.Scaleform.daapi.view.meta.RespawnMinimapMeta import RespawnMinimapMeta
from ids_generators import Int32IDGenerator
from helpers import dependency, isPlayerAvatar
from skeletons.gui.battle_session import IBattleSessionProvider
from PlayerEvents import g_playerEvents
_C_NAME = settings.CONTAINER_NAME
_S_NAME = settings.ENTRY_SYMBOL_NAME
_RESPAWN_SYMBOL_NAME = 'EventRespawnPointEntryUI'
_LOOT_AMMO_SYMBOL_NAME = 'EventAmmoMinimapEntryUI'
_SECTOR_SYMBOL_NAME = 'EventSectorMinimapEntryUI'
_RESPAWN_MAP_PATH = '_level0.root.{}.main.vehicleSelector.respawnMinimap.entriesContainer'.format(APP_CONTAINERS_NAMES.VIEWS)
_IMAGE_PATH_FORMATTER = 'img://{}'

class EventPersonalEntriesPlugin(PersonalEntriesPlugin):

    def _onKillerVisionExit(self):
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None and ctrl.playerLives <= 0:
            self.setKillerVehicleID(0)
            self.updateControlMode(CTRL_MODE_NAME.DEATH_FREE_CAM, 0)
        else:
            super(EventPersonalEntriesPlugin, self)._onKillerVisionExit()
        return


class LineOfFrontInDangerousPlugin(EntriesPlugin):
    __slots__ = ('__callbackIDs', '__idGenerator')
    _ANIMATION_NAME = 'firstEnemy'
    _MINIMAP_NOTIFICATION_DURATION = 3

    def __init__(self, parent):
        super(LineOfFrontInDangerousPlugin, self).__init__(parent, clazz=VehicleEntry)
        self.__callbackIDs = {}
        self.__idGenerator = Int32IDGenerator()

    def stop(self):
        self.__clearAllCallbacks()
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onVehicleEnteredDangerZone -= self.__showDangerPosition
        super(LineOfFrontInDangerousPlugin, self).stop()

    def start(self):
        super(LineOfFrontInDangerousPlugin, self).start()
        if isPlayerAvatar():
            player = BigWorld.player()
            player.onVehicleEnteredDangerZone += self.__showDangerPosition

    def __showDangerPosition(self, position):
        matrix = minimap_utils.makePositionMatrix(position)
        uniqueID = self.__idGenerator.next()
        model = self._addEntryEx(uniqueID, _S_NAME.VEHICLE, _C_NAME.ALIVE_VEHICLES, matrix=matrix, active=True)
        self._invoke(model.getID(), 'setVehicleInfo', '', '', '', '', self._ANIMATION_NAME)
        self._playSound2D(settings.MINIMAP_ATTENTION_SOUND_ID)
        self.__scheduleCleanup(uniqueID, self._MINIMAP_NOTIFICATION_DURATION)

    def __scheduleCleanup(self, uniqueID, interval):
        self.__clearCallback(uniqueID)
        self.__callbackIDs[uniqueID] = BigWorld.callback(interval, partial(self.__clearCallback, uniqueID))

    def __clearCallback(self, uniqueID):
        callbackID = self.__callbackIDs.pop(uniqueID, None)
        if callbackID is not None:
            self._delEntryEx(uniqueID)
            BigWorld.cancelCallback(callbackID)
        return

    def __clearAllCallbacks(self):
        for uniqueID, callbackID in self.__callbackIDs.iteritems():
            self._delEntryEx(uniqueID)
            BigWorld.cancelCallback(callbackID)

        self.__callbackIDs.clear()


class EventTeamsPointsPlugin(EntriesPlugin):
    __slots__ = ('__respawns', '__selectedGroupID', '__boundingBox')
    _INITIAL_SELECTED_GROUP_ID = 1

    def __init__(self, parentObj):
        super(EventTeamsPointsPlugin, self).__init__(parentObj)
        self.__respawns = {}
        self.__selectedGroupID = self._INITIAL_SELECTED_GROUP_ID
        self.__boundingBox = (Math.Vector2(0, 0), Math.Vector2(0, 0))

    def start(self):
        super(EventTeamsPointsPlugin, self).start()
        self.__boundingBox = self.sessionProvider.arenaVisitor.type.getPlayerBoundingBox()
        respawnCtrl = self.sessionProvider.dynamic.respawn
        if respawnCtrl:
            respawnCtrl.onAddRespawnGroup += self.__addRespawnGroup
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        if periodCtrl.getPeriod() == ARENA_PERIOD.BATTLE and respawnCtrl:
            for groupID, (position, isSelected) in respawnCtrl.respawnGroups.iteritems():
                self.__addRespawnGroup(groupID, position, isSelected)

    def stop(self):
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl:
            ctrl.onAddRespawnGroup -= self.__addRespawnGroup
        super(EventTeamsPointsPlugin, self).stop()

    def onMinimapClick(self, x, y):
        if not self.__respawns:
            return
        matrix = minimap_utils.makePointMatrixByLocal(x, y, *self.__boundingBox)
        clickPoint = matrix.translation
        minDistance = 0
        for groupID, respawn in self.__respawns.iteritems():
            self._invoke(respawn['entryID'], 'setSelected', False)
            distance = (respawn['position'] - clickPoint).length
            if minDistance == 0 or distance < minDistance:
                minDistance = distance
                self.__selectedGroupID = groupID

        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl:
            ctrl.selectRespawnGroup(self.__selectedGroupID)
        self._invoke(self.__respawns[self.__selectedGroupID]['entryID'], 'setSelected', True)

    def __addRespawnGroup(self, groupID, position, isSelected):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        entryID = self._addEntry(_RESPAWN_SYMBOL_NAME, _C_NAME.TEAM_POINTS, matrix=matrix, active=True)
        if entryID:
            self.__respawns[groupID] = {'entryID': entryID,
             'position': position}
            self._invoke(entryID, 'setPointNumber', groupID - 1)
            self._invoke(entryID, 'setSelected', isSelected)
            if isSelected:
                self.__selectedGroupID = groupID


class EventMinimapComponent(ClassicMinimapComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def _setupPlugins(self, arenaVisitor):
        setup = super(EventMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['personal'] = EventPersonalEntriesPlugin
        setup['lof_danger_zone'] = LineOfFrontInDangerousPlugin
        setup['loot_objects'] = LootObjectsExtendedPlugin
        return setup

    def _populate(self):
        super(EventMinimapComponent, self)._populate()
        self.as_setOverlayS(_IMAGE_PATH_FORMATTER.format(self.sessionProvider.arenaVisitor.type.getMinimapArrowsTexture()))


class EventRespawnMinimapComponent(EventMinimapComponent, RespawnMinimapMeta):

    def onMinimapClick(self, x, y):
        plugin = self.getPlugin('points')
        if plugin:
            plugin.onMinimapClick(x, y)

    def _setupPlugins(self, arenaVisitor):
        setup = super(EventRespawnMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['points'] = EventTeamsPointsPlugin
        setup['loot_objects'] = LootObjectsEntriesPlugin
        setup['settings'] = EventRespawnSettingsPlugin
        setup['personal'] = EventRespawnPersonalEntriesPlugin
        return setup

    def _createFlashComponent(self):
        return GUI.WGMinimapFlashAS3(self.app.movie, _RESPAWN_MAP_PATH)

    def _getFlashName(self):
        pass


class EventRespawnPersonalEntriesPlugin(PersonalEntriesPlugin):
    __slots__ = ('__isFirstSpawn',)

    def __init__(self, parentObj):
        super(EventRespawnPersonalEntriesPlugin, self).__init__(parentObj)
        self.__isFirstSpawn = True

    def start(self):
        super(EventRespawnPersonalEntriesPlugin, self).start()
        self.__isFirstSpawn = self.sessionProvider.shared.arenaPeriod.getPeriod() != ARENA_PERIOD.BATTLE
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange

    def stop(self):
        super(EventRespawnPersonalEntriesPlugin, self).stop()
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange

    def _enableCameraEntryInCtrlMode(self, ctrlMode):
        return False

    def _isActiveViewRangeCircle(self):
        return self.__isFirstSpawn

    def _isActiveViewPoint(self, vehicleID):
        return self.__isFirstSpawn

    def _isActiveDeadPoint(self):
        return False

    def _updateCirlcesState(self):
        pass

    def _showCircles(self, showCircles):
        super(EventRespawnPersonalEntriesPlugin, self)._showCircles(showCircles and self.__isFirstSpawn)

    def _invalidateMarkup(self, forceInvalidate=False):
        if self.__isFirstSpawn:
            super(EventRespawnPersonalEntriesPlugin, self)._invalidateMarkup(forceInvalidate)

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if self.__isFirstSpawn and period == ARENA_PERIOD.BATTLE:
            self.__isFirstSpawn = False


class LootObjectsEntriesPlugin(EntriesPlugin):
    __slots__ = ('_lootDict',)

    def __init__(self, parentObj):
        super(LootObjectsEntriesPlugin, self).__init__(parentObj)
        self._lootDict = {}

    def start(self):
        super(LootObjectsEntriesPlugin, self).start()
        self._updateCurrentOpacity()
        lootComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'loot', None)
        if lootComp is not None:
            lootComp.onLootAdded += self.__onLootAdded
            lootComp.onLootRemoved += self.__onLootRemoved
            lootEntities = lootComp.getLootEntities()
            for loot in lootEntities.values():
                self.__onLootAdded(loot)

        return

    def fini(self):
        lootComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'loot', None)
        if lootComp is not None:
            lootComp.onLootAdded -= self.__onLootAdded
            lootComp.onLootRemoved -= self.__onLootRemoved
        super(LootObjectsEntriesPlugin, self).fini()
        return

    def _updateCurrentOpacity(self):
        pass

    def _setLootHighlight(self, lootEntryID):
        self._invoke(lootEntryID, 'setHighlight', False)

    def __onLootRemoved(self, loot):
        if loot.id in self._lootDict:
            self._delEntry(self._lootDict[loot.id])
            del self._lootDict[loot.id]

    def __onLootAdded(self, loot):
        minimapSymbol = loot.gameObject.minimapSymbol
        if minimapSymbol is not None:
            matrix = Math.Matrix()
            matrix.setTranslate(loot.position)
            lootEntryID = self._addEntry(minimapSymbol, _C_NAME.ICONS, matrix=matrix, active=True)
            self._lootDict[loot.id] = lootEntryID
            if minimapSymbol == _LOOT_AMMO_SYMBOL_NAME:
                self._setLootHighlight(lootEntryID)
        return


class LootObjectsExtendedPlugin(LootObjectsEntriesPlugin):
    __slots__ = ('__ammoHighlight',)

    def __init__(self, parentObj):
        super(LootObjectsExtendedPlugin, self).__init__(parentObj)
        self.__ammoHighlight = False

    def start(self):
        super(LootObjectsExtendedPlugin, self).start()
        lootSign = self.sessionProvider.dynamic.lootSign
        if lootSign is not None:
            lootSign.onLootSignUpdated += self.__onLootSignUpdated
        return

    def fini(self):
        lootSign = self.sessionProvider.dynamic.lootSign
        if lootSign is not None:
            lootSign.onLootSignUpdated -= self.__onLootSignUpdated
        super(LootObjectsExtendedPlugin, self).fini()
        return

    def _updateCurrentOpacity(self):
        lootComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'loot', None)
        lootSign = self.sessionProvider.dynamic.lootSign
        prevValue = self.__ammoHighlight
        self.__ammoHighlight = lootSign is not None and lootSign.showLootSign
        if self.__ammoHighlight != prevValue:
            for lootID in self._lootDict.iterkeys():
                loot = lootComp.getLootByID(lootID)
                minimapSymbol = loot.gameObject.minimapSymbol
                if minimapSymbol == _LOOT_AMMO_SYMBOL_NAME:
                    self._setLootHighlight(self._lootDict[lootID])

        return

    def _setLootHighlight(self, lootEntryID):
        self._invoke(lootEntryID, 'setHighlight', self.__ammoHighlight)

    def __onLootSignUpdated(self):
        self._updateCurrentOpacity()


class EventRespawnSettingsPlugin(GlobalSettingsPlugin):

    def _isHotKeysDisabled(self):
        return True
