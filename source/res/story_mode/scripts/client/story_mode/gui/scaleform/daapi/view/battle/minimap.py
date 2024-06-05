# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/minimap.py
import typing
import BigWorld
import CGF
import Math
from BunkerLogicComponent import BunkerLogicComponent
from constants import IS_DEVELOPMENT
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicTeleportPlugin
from gui.Scaleform.daapi.view.battle.pve_base.minimap import PveMinimapComponent, PveMinimapGlobalSettingsPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.common import SimplePlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.entries import VehicleEntry
from gui.Scaleform.daapi.view.battle.shared.minimap.plugins import ArenaVehiclesPlugin
from gui.Scaleform.daapi.view.battle.shared.minimap.settings import CONTAINER_NAME
from gui.battle_control import avatar_getter
from gui.impl import backport
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from Math import Vector2
_MINIMAP_DIMENSIONS = 10
_ANIMATION_SPG = 'enemySPG'
_ANIMATION_ENEMY = 'firstEnemy'
_BUNKER_SYMBOL = 'BunkerMinimapEntryUI'

class StoryModeVehicleEntry(VehicleEntry):
    __slots__ = ()

    def getSpottedAnimation(self, pool):
        if self._isEnemy and self._isActive and self._isInAoI:
            if self.getActualSpottedCount() == 1:
                if self._classTag == 'SPG':
                    return _ANIMATION_SPG
                return _ANIMATION_ENEMY


class StoryModeArenaVehiclesPlugin(ArenaVehiclesPlugin):
    __slots__ = ()

    def __init__(self, parent):
        super(StoryModeArenaVehiclesPlugin, self).__init__(parent=parent, clazz=StoryModeVehicleEntry)


class BunkersPlugin(SimplePlugin):
    __slots__ = ('__bunkersDict', '_distanceUpdateCallback')
    _DISTANCE_UPDATE_TIME = 1

    def __init__(self, parentObj):
        super(BunkersPlugin, self).__init__(parentObj)
        self.__bunkersDict = {}
        self._distanceUpdateCallback = None
        return

    def start(self):
        super(BunkersPlugin, self).start()
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is not None:
            destructibleComponent.onDestructibleEntityAdded += self.__onDestructibleEntityAdded
            destructibleComponent.onDestructibleEntityHealthChanged += self.__onDestructibleEntityHealthChanged
            entities = destructibleComponent.destructibleEntities
            for entity in (entity for _, entity in entities.iteritems() if entity.destructibleEntityID != 0):
                self.__onDestructibleEntityAdded(entity)

        return

    def fini(self):
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is not None:
            destructibleComponent.onDestructibleEntityAdded -= self.__onDestructibleEntityAdded
            destructibleComponent.onDestructibleEntityHealthChanged -= self.__onDestructibleEntityHealthChanged
        if self._distanceUpdateCallback is not None:
            BigWorld.cancelCallback(self._distanceUpdateCallback)
            self._distanceUpdateCallback = None
        super(BunkersPlugin, self).fini()
        return

    def __onDestructibleEntityAdded(self, entity):
        entryID = self.__bunkersDict[entity.destructibleEntityID] = self.__addBunkerEntry(entity.position)
        isDead = entity.health == 0
        if entryID is not None:
            self._invoke(entryID, 'setName', backport.text(R.strings.sm_battle.bunker()))
            self._invoke(entryID, 'setDead', isDead)
        self._updateDistanceToEntity(entryID, entity)
        if self._distanceUpdateCallback is None:
            self._distanceUpdateCallback = BigWorld.callback(self._DISTANCE_UPDATE_TIME, self._distanceUpdate)
        return

    def _updateDistanceToEntity(self, entityId, entity):
        if entity.health == 0:
            self._setActive(entityId, True)
        elif entity.isActive:
            bunkerQuery = CGF.Query(BigWorld.player().spaceID, (CGF.GameObject, BunkerLogicComponent))
            bunkerLogic = next((bunker for _, bunker in bunkerQuery if bunker.destructibleEntityId == entity.destructibleEntityID), None)
            if bunkerLogic:
                distance = (entity.position - avatar_getter.getOwnVehiclePosition()).length
                self._setActive(entityId, distance < bunkerLogic.markerDistance)
        else:
            self._setActive(entityId, False)
        return

    def _distanceUpdate(self):
        destructibleComponent = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if destructibleComponent is None:
            self._distanceUpdateCallback = None
            return
        else:
            for entityId in destructibleComponent.destructibleEntities:
                entity = destructibleComponent.getDestructibleEntity(entityId)
                if entity is None:
                    continue
                entryID = self.__bunkersDict.get(entityId, None)
                if entryID:
                    self._updateDistanceToEntity(entryID, entity)

            self._distanceUpdateCallback = BigWorld.callback(self._DISTANCE_UPDATE_TIME, self._distanceUpdate)
            return

    def __onDestructibleEntityHealthChanged(self, destructibleEntityID, newHealth, maxHealth, atkID, atkReason, hitFlags):
        if newHealth != 0:
            return
        else:
            entryID = self.__bunkersDict.get(destructibleEntityID, None)
            if entryID is not None:
                self._invoke(entryID, 'setDead', True)
                self._move(entryID, CONTAINER_NAME.DEAD_VEHICLES)
            return

    def __addBunkerEntry(self, position):
        matrix = Math.Matrix()
        matrix.setTranslate(position)
        entryID = self._addEntry(_BUNKER_SYMBOL, CONTAINER_NAME.ALIVE_VEHICLES, matrix=matrix, active=True)
        return entryID


class StoryModeMinimapComponent(PveMinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(StoryModeMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['settings'] = PveMinimapGlobalSettingsPlugin
        setup['vehicles'] = StoryModeArenaVehiclesPlugin
        setup['bunkers'] = BunkersPlugin
        if IS_DEVELOPMENT:
            setup['teleport'] = ClassicTeleportPlugin
        return setup

    def hasMinimapGrid(self):
        return True

    def getMinimapDimensions(self):
        return _MINIMAP_DIMENSIONS

    def getBoundingBox(self):
        arenaVisitor = self.sessionProvider.arenaVisitor
        return adjustBoundingBox(*arenaVisitor.type.getBoundingBox())


def adjustBoundingBox(bl, tr):
    topRightX, topRightY = tr
    bottomLeftX, bottomLeftY = bl
    vSide = topRightX - bottomLeftX
    hSide = topRightY - bottomLeftY
    if vSide > hSide:
        bl = (bottomLeftX, bottomLeftX)
        tr = (topRightX, topRightX)
    else:
        bl = (bottomLeftY, bottomLeftY)
        tr = (topRightY, topRightY)
    return (bl, tr)
