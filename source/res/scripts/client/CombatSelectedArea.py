# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CombatSelectedArea.py
import BigWorld
import Math
from AvatarInputHandler import mathUtils
from constants import SERVER_TICK_LENGTH
OVER_TERRAIN_HEIGHT = 0.5
MARKER_HEIGHT = 5.0
DEFAULT_RADIUS_MODEL = 'content/Interface/CheckPoint/CheckPoint.visual'
DEFAULT_ROTATE_MODEL = 'content/Interface/TargetPoint/rectangle2_1.visual'
COLOR_WHITE = 4294967295L

class CombatSelectedArea(object):
    position = property(lambda self: self.__matrix.translation)

    def __init__(self, enableConstrainToArenaBounds=False):
        self.__terrainSelectedArea = None
        self.__pixelQuad = None
        self.__terrainRotatedArea = None
        self.__fakeModel = None
        self.__overTerrainHeight = OVER_TERRAIN_HEIGHT
        self.__matrix = None
        self.__rotateModelNode = None
        self.__color = None
        self.__size = None
        self.__enableConstrainToArenaBounds = enableConstrainToArenaBounds
        return

    def setup(self, position, direction, size, visualPath, color, marker):
        self.__fakeModel = model = BigWorld.Model('')
        rootNode = model.node('')
        self.__terrainSelectedArea = area = BigWorld.PyTerrainSelectedArea()
        area.setup(visualPath, size, self.__overTerrainHeight, color)
        area.enableAccurateCollision(True)
        area.setYCutOffDistance(MARKER_HEIGHT)
        rootNode.attach(area)
        self.__size = size
        self.__color = color
        BigWorld.addModel(model)
        self.__matrix = Math.Matrix()
        model.addMotor(BigWorld.Servo(self.__matrix))
        self.relocate(position, direction)
        self.__nextPosition = position
        self.__speed = Math.Vector3(0.0, 0.0, 0.0)
        self.__time = 0.0

    def addLine(self, position, color, width, height):
        if self.__fakeModel is None:
            self.__fakeModel = BigWorld.Model('')
        rootNode = self.__fakeModel.node('')
        self.__pixelQuad = BigWorld.PyStrictPixelQuad()
        self.__pixelQuad.setup(width, height, color, position)
        rootNode.attach(self.__pixelQuad)
        return

    def setSelectingDirection(self, value=False):
        if value and self.__terrainRotatedArea is None:
            objectSize = Math.Vector2(10.0, 10.0)
            self.__rotateModelNode = self.__fakeModel.node('', mathUtils.createRTMatrix(Math.Vector3(-self.__matrix.yaw, 0.0, 0.0), Math.Vector3((-self.__size.x - objectSize.x) * 0.5, 0.0, (self.__size.y + objectSize.y) * 0.5)))
            self.__terrainRotatedArea = area = BigWorld.PyTerrainSelectedArea()
            area.setup(DEFAULT_ROTATE_MODEL, objectSize, self.__overTerrainHeight, self.__color)
            area.enableAccurateCollision(True)
            area.setYCutOffDistance(MARKER_HEIGHT)
            self.__rotateModelNode.attach(area)
        elif not value and self.__terrainRotatedArea is not None:
            self.__rotateModelNode.detach(self.__terrainRotatedArea)
            self.__terrainRotatedArea = None
        return

    def setConstrainToArenaBounds(self, enable):
        self.__enableConstrainToArenaBounds = enable

    def setOverTerrainOffset(self, offset):
        if self.__terrainSelectedArea is not None:
            self.__terrainSelectedArea.setOverTerrainOffset(offset)
        if self.__terrainRotatedArea is not None:
            self.__terrainRotatedArea.setOverTerrainOffset(offset)
        return

    def relocate(self, position, direction):
        if position is None:
            return
        else:
            self.__matrix.setRotateYPR((direction.yaw, 0, 0))
            self.__matrix.translation = position
            if self.__enableConstrainToArenaBounds:
                halfX = self.__size.x * 0.5
                halfY = self.__size.y * 0.5
                corners = {(halfX, 0, halfY),
                 (-halfX, 0, halfY),
                 (-halfX, 0, -halfY),
                 (halfX, 0, -halfY)}
                transformedCorners = map(lambda corner: self.__matrix.applyPoint(corner), corners)
                arena = BigWorld.player().arena
                correction = Math.Vector3(0)
                for transformedCorner in transformedCorners:
                    if not arena.isPointInsideArenaBB(transformedCorner):
                        correctedPoint = arena.getClosestPointOnArenaBB(transformedCorner)
                        correction.x = max(correction.x, correctedPoint.x - transformedCorner.x, key=abs)
                        correction.z = max(correction.z, correctedPoint.z - transformedCorner.z, key=abs)

                self.__matrix.translation = position + correction
            self.__terrainSelectedArea.updateHeights()
            if self.__terrainRotatedArea:
                self.__terrainRotatedArea.updateHeights()
            return

    def setGUIVisible(self, isVisible):
        self.__fakeModel.visible = isVisible

    def setNextPosition(self, nextPosition, direction):
        self.relocate(self.__nextPosition, direction)
        self.__speed = (nextPosition - self.__nextPosition) / SERVER_TICK_LENGTH
        self.__nextPosition = nextPosition
        self.__time = 0.0

    def update(self, deltaTime):
        if self.__time <= SERVER_TICK_LENGTH:
            self.__matrix.translation = self.__matrix.translation + self.__speed * deltaTime
            self.__time += deltaTime
        else:
            self.__matrix.translation = self.__nextPosition

    def setupDefault(self, position, direction, size, marker):
        self.setup(position, direction, size, DEFAULT_RADIUS_MODEL, COLOR_WHITE, marker)

    def destroy(self):
        BigWorld.delModel(self.__fakeModel)
        self.__terrainSelectedArea = None
        self.__terrainRotatedArea = None
        self.__pixelQuad = None
        self.__fakeModel = None
        self.__matrix = None
        self.__rotateModelNode = None
        return

    def pointInside(self, point):
        m = Math.Matrix(self.__fakeModel.matrix)
        m.invert()
        point = m.applyPoint(point)
        x_side = self.__size.x / 2
        y_side = self.__size.y / 2
        return -x_side < point.x < x_side and -y_side < point.z < y_side
