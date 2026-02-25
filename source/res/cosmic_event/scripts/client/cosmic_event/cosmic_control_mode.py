# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/cosmic_control_mode.py
import BigWorld
import Math
from AvatarInputHandler.MapCaseMode import _ArenaBoundsAreaStrikeSelector
from AvatarInputHandler.control_modes import ArcadeControlMode
from AvatarInputHandler import AimingSystems
from cosmic_camera import CosmicCamera
from cosmic_event_common.cosmic_constants import MINE_ENTITY_NAME
TOP_TERRAIN_HEIGHT = 65
BOT_Y = 0

def rescanPosition(position):
    top = Math.Vector3(position.x, TOP_TERRAIN_HEIGHT, position.z)
    bot = Math.Vector3(position.x, BOT_Y, position.z)
    terrainPos = AimingSystems.__collideStaticOnly(top, bot)
    if terrainPos is not None:
        pos = terrainPos[0]
        return pos
    else:
        return


class _CosmicArenaBoundStrikeSelector(_ArenaBoundsAreaStrikeSelector):

    def __init__(self, *args, **kwargs):
        super(_CosmicArenaBoundStrikeSelector, self).__init__(*args, **kwargs)
        self.area.enableWaterCollision(True)
        self.area.setMaxHeight(TOP_TERRAIN_HEIGHT)

    def processSelection(self, position, reset=False):
        position = rescanPosition(position)
        return super(_CosmicArenaBoundStrikeSelector, self).processSelection(position, reset) if position is not None else False


class _CosmicArenaMineSelector(_CosmicArenaBoundStrikeSelector):

    def __init__(self, position, equipment):
        super(_CosmicArenaMineSelector, self).__init__(position, equipment)
        self.__checkIntersectMines()

    def processSelection(self, position, reset=False):
        if not reset:
            if self.isIntersectMine():
                return False
        return super(_CosmicArenaMineSelector, self).processSelection(position, reset)

    def tick(self):
        super(_CosmicArenaMineSelector, self).tick()
        self.__checkIntersectMines()

    def isIntersectMine(self):
        allMines = [ e for e in BigWorld.entities.values() if e.__class__.__name__ == MINE_ENTITY_NAME and not e.isDetonated ]
        return any(self.__minesIntersected(allMines))

    def __minesIntersected(self, mines):
        for m in mines:
            if self.area.pointInside(m.position):
                yield m

    def __checkIntersectMines(self):
        if self.isIntersectMine():
            self.area.setColor(self.equipment.restrictedAreaColor)
        else:
            self.area.setColor()


class CosmicControlMode(ArcadeControlMode):

    def _setupCamera(self, dataSection):
        self._cam = CosmicCamera(dataSection['camera'], defaultOffset=self._defaultOffset)
