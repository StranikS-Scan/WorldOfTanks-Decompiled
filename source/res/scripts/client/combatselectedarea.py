# Embedded file name: scripts/client/CombatSelectedArea.py
import BigWorld
import Math
from AvatarInputHandler import mathUtils
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG
from gui.WindowsManager import g_windowsManager
from constants import SERVER_TICK_LENGTH
OVER_TERRAIN_HEIGHT = 0.5
MARKER_HEIGHT = 5.0
DEFAULT_RADIUS_MODEL = 'content/Interface/CheckPoint/CheckPoint.visual'
COLOR_WHITE = 4294967295L

class CombatSelectedArea(object):
    position = property(lambda self: self.__fakeModel.position)

    def __init__(self):
        self.__terrainSelectedArea = None
        self.__fakeModel = None
        self.__marker = None
        return

    def setup(self, position, direction, size, visualPath, color, marker):
        self.__fakeModel = model = BigWorld.player().newFakeModel()
        model.position = position
        model.yaw = direction.yaw
        BigWorld.addModel(model)
        rootNode = model.node('')
        self.__terrainSelectedArea = area = BigWorld.PyTerrainSelectedArea()
        area.setup(visualPath, size, OVER_TERRAIN_HEIGHT, color)
        rootNode.attach(area)
        markerTranslation = mathUtils.MatrixProviders.product(rootNode, mathUtils.createTranslationMatrix(Math.Vector3(0.0, MARKER_HEIGHT, 0.0)))
        self.__nextPosition = position
        self.__speed = Math.Vector3(0.0, 0.0, 0.0)
        self.__time = 0.0

    def relocate(self, position, direction):
        self.__fakeModel.position = position
        self.__fakeModel.yaw = direction.yaw
        self.__terrainSelectedArea.updateHeights()

    def setNextPosition(self, nextPosition, direction):
        self.relocate(self.__nextPosition, direction)
        self.__speed = (nextPosition - self.__nextPosition) / SERVER_TICK_LENGTH
        self.__nextPosition = nextPosition
        self.__time = 0.0

    def update(self, deltaTime):
        if self.__time <= SERVER_TICK_LENGTH:
            self.__fakeModel.position = self.__fakeModel.position + self.__speed * deltaTime
            self.__time += deltaTime
        else:
            self.__fakeModel.position = self.__nextPosition

    def setupDefault(self, position, direction, size, marker):
        self.setup(position, direction, size, DEFAULT_RADIUS_MODEL, COLOR_WHITE, marker)

    def destroy(self):
        BigWorld.delModel(self.__fakeModel)
        self.__terrainSelectedArea = None
        self.__fakeModel = None
        self.__marker = None
        return
