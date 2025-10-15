# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/avatar_input_handler/portal_map_case_mode.py
import BigWorld
from AvatarInputHandler import MapCaseMode
from Math import Vector2
from portal.sounds.sound_constants import PortalUISound
from portal.sounds.sound_helpers import play2DSound

class PortalStrikeSelector(MapCaseMode._ArcadeBomberStrikeSelector):
    pass


class SentryGunPortalSelector(MapCaseMode._ArcadeBomberStrikeSelector):
    __OBSTACLES_CLASS_NAMES = ('Vehicle',)
    __DEFAULT_BOUNDING_RADIUS = 8
    __BOUNDING_OFFSET = 2

    def __init__(self, position, equipment):
        MapCaseMode._ArcadeBomberStrikeSelector.__init__(self, position, equipment)
        self.__checkIntersectObstacle()

    def processSelection(self, position, reset=False):
        if not reset and self.isIntersectObstacle():
            play2DSound(PortalUISound.NOT_APPLY_SOUND)
            return False
        return MapCaseMode._ArcadeBomberStrikeSelector.processSelection(self, position, reset)

    def tick(self):
        super(SentryGunPortalSelector, self).tick()
        self.__checkIntersectObstacle()

    def isIntersectObstacle(self):
        obstacles = [ e for e in BigWorld.entities.values() if e.__class__.__name__ in self.__OBSTACLES_CLASS_NAMES ]
        return any(self.__obstacleIntersected(obstacles))

    def __obstacleIntersected(self, obstacles):
        for obstacle in obstacles:
            obstacleBoundingRadius = self.__DEFAULT_BOUNDING_RADIUS
            if hasattr(obstacle, 'typeDescriptor'):
                hullBboxMin, hullBboxMax, _ = obstacle.typeDescriptor.hull.hitTester.bbox
                obstacleBoundingRadius = Vector2(hullBboxMax.x - hullBboxMin.x, hullBboxMax.z - hullBboxMin.z).length
            if abs(self.area.position.y - obstacle.position.y > 50):
                continue
            if self.area.pointInsideCircle(obstacle.position, obstacleBoundingRadius + self.__BOUNDING_OFFSET):
                yield obstacle

    def __checkIntersectObstacle(self):
        if self.isIntersectObstacle():
            self.area.setColor(int(4290649856L))
        else:
            self.area.setColor(int(4287615196L))


class MinefieldPortalSelector(MapCaseMode._ArcadeBomberStrikeSelector, MapCaseMode._FLMinesSensor):

    def __init__(self, position, equipment):
        MapCaseMode._ArcadeBomberStrikeSelector.__init__(self, position, equipment)
        MapCaseMode._FLMinesSensor.__init__(self, self.__minesIntersected)
        self.__checkIntersectMines()

    def destroy(self):
        MapCaseMode._ArcadeBomberStrikeSelector.destroy(self)
        MapCaseMode._FLMinesSensor.destroy(self)

    def processSelection(self, position, reset=False):
        if not reset and self.isIntersectMine():
            play2DSound(PortalUISound.NOT_APPLY_SOUND)
            ctrl = self._sessionProvider.shared.messages
            if ctrl is not None:
                ctrl.showVehicleError('minefieldIsIntersected')
            return False
        else:
            return MapCaseMode._ArcadeBomberStrikeSelector.processSelection(self, position, reset)

    def tick(self):
        super(MinefieldPortalSelector, self).tick()
        self.__checkIntersectMines()

    def __minesIntersected(self, mines):
        for m in mines:
            if self.area.pointInside(m.position):
                yield m

    def __checkIntersectMines(self):
        if self.isIntersectMine():
            self.area.setColor(int(4290649856L))
        else:
            self.area.setColor(int(4287615196L))


class PortalVehicleTrapSelector(MapCaseMode._ArenaBoundsAreaStrikeSelector):
    pass
