# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/BorderVisual.py
import math
from collections import namedtuple
import BigWorld
import ResMgr
from epic_constants import SECTOR_EDGE_STATE
from items import _xml
from Math import Matrix, Vector3
import math_utils
CONFIG_FILE = 'scripts/dynamic_objects.xml'
BORDER_VISUAL_TAG = 'SectorBorderVisual'
VisualSetting = namedtuple('VisualSetting', ('modelPath', 'overTerrainHeight', 'modelSettings'))
ModelSetting = namedtuple('ModelSetting', ('scale', 'spacing', 'color'))
DashesParams = namedtuple('DashesParams', ('size', 'color', 'shift', 'offset'))

def _readModelSetting(ctx, section):
    return ModelSetting(scale=_xml.readVector3(ctx, section, 'scale'), spacing=_xml.readFloat(ctx, section, 'spacing'), color=int(_xml.readString(ctx, section, 'color'), 0))


def _readVisualSettings():
    ctx = (None, CONFIG_FILE + '/' + BORDER_VISUAL_TAG)
    settings = ResMgr.openSection(CONFIG_FILE)[BORDER_VISUAL_TAG]
    return VisualSetting(modelPath=_xml.readString(ctx, settings, 'modelPath'), overTerrainHeight=_xml.readFloat(ctx, settings, 'overTerrainHeight'), modelSettings={getattr(SECTOR_EDGE_STATE, item[1][1]['edgeState'].asString.upper()):_readModelSetting(*item[1]) for item in _xml.getItemsWithContext(ctx, settings, 'modelSetting') if SECTOR_EDGE_STATE.hasKey(item[1][1]['edgeState'].asString.upper())})


g_borderVisualSettings = _readVisualSettings()

class BorderVisual(object):
    __DEFAULT_DASH_SIZE = (1, 1)
    __DEFAULT_DASH_COLOR = 4294967295L

    def __init__(self):
        self.__direction = None
        self.__length = None
        self.__numModelsPerEdgeState = None
        self.__terrainModels = None
        self.__attachNodes = None
        self.__modelOffsets = None
        self.__rootModel = None
        self.__rootMatrix = None
        self.__edgeState = None
        return

    def create(self, fromPos, toPos, currentEdgeState=SECTOR_EDGE_STATE.NONE):
        if None in (fromPos, toPos):
            return
        else:
            self.__edgeState = currentEdgeState
            if not BigWorld.player().arena.isPointInsideArenaBB(fromPos):
                fromPos = BigWorld.player().arena.getClosestPointOnArenaBB(fromPos)
            if not BigWorld.player().arena.isPointInsideArenaBB(toPos):
                toPos = BigWorld.player().arena.getClosestPointOnArenaBB(toPos)
            self.__direction = toPos - fromPos
            self.__length = self.__direction.length
            self.__direction.normalise()
            self.__numModelsPerEdgeState = {}
            for edgeState, modelSetting in g_borderVisualSettings.modelSettings.iteritems():
                dashLength = modelSetting.scale.x
                gap = modelSetting.spacing
                self.__numModelsPerEdgeState[edgeState] = max(1, int((self.__length - 2 * dashLength) / (dashLength + gap)) + 1)

            maxNumModels = max(self.__numModelsPerEdgeState.values())
            rotation = (self.__direction.yaw + math.pi * 0.5, self.__direction.pitch, 0.0)
            translation = fromPos + self.__direction * self.__length * 0.5
            self.__rootMatrix = rootMatrix = math_utils.createRTMatrix(rotation=rotation, translation=translation)
            self.__rootModel = rootModel = BigWorld.Model('')
            rootModel.addMotor(BigWorld.Servo(rootMatrix))
            BigWorld.player().addModel(rootModel)
            self.__terrainModels = [None] * maxNumModels
            self.__attachNodes = [None] * maxNumModels
            self.__modelOffsets = [None] * maxNumModels
            dashesParams = self.__getDashesParams(currentEdgeState)
            for idx in range(0, maxNumModels):
                self.__terrainModels[idx] = area = BigWorld.PyTerrainSelectedArea()
                self.__modelOffsets[idx] = offset = Matrix()
                self.__attachNodes[idx] = attachNode = rootModel.node('', offset)
                attachNode.attach(area)
                area.setup(g_borderVisualSettings.modelPath, dashesParams.size, g_borderVisualSettings.overTerrainHeight, dashesParams.color)
                area.enableYCutOff(False)
                area.enableAccurateCollision(False)
                offset.translation = dashesParams.offset
                dashesParams.offset.x += dashesParams.shift

            return

    def destroy(self):
        for model, node in zip(self.__terrainModels, self.__attachNodes):
            if model.attached:
                node.detach(model)

        self.__attachNodes = None
        self.__modelOffsets = None
        self.__terrainModels = None
        self.__rootMatrix = None
        if self.__rootModel.inWorld:
            BigWorld.player().delModel(self.__rootModel)
        self.__rootModel = None
        self.__numModelsPerEdgeState = None
        self.__length = None
        self.__direction = None
        return

    def showState(self, edgeState):
        if edgeState == SECTOR_EDGE_STATE.NONE:
            for terrainModel in self.__terrainModels:
                if terrainModel.attached:
                    terrainModel.setVisible(False)

            return
        for terrainModel in self.__terrainModels:
            if terrainModel.attached:
                terrainModel.setVisible(True)

        if self.__edgeState == edgeState:
            return
        self.__edgeState = edgeState
        numModels = self.__numModelsPerEdgeState[edgeState]
        dashesParams = self.__getDashesParams(edgeState)
        for terrainModel, attachNode, offset in zip(self.__terrainModels, self.__attachNodes, self.__modelOffsets):
            terrainModel.setColor(dashesParams.color)
            if not terrainModel.attached:
                attachNode.attach(terrainModel)
                terrainModel.setVisible(True)
            offset.translation = dashesParams.offset
            terrainModel.setSize(dashesParams.size)
            terrainModel.updateHeights()
            dashesParams.offset.x += dashesParams.shift

        for idx in range(numModels, len(self.__attachNodes)):
            if self.__terrainModels[idx].attached:
                self.__attachNodes[idx].detach(self.__terrainModels[idx])
                self.__terrainModels[idx].setVisible(False)
            break

    def __getDashesParams(self, edgeState):
        if edgeState != SECTOR_EDGE_STATE.NONE:
            modelSetting = g_borderVisualSettings.modelSettings[edgeState]
            size = (modelSetting.scale.x, modelSetting.scale.z)
            color = modelSetting.color
            gap = modelSetting.spacing
            length = modelSetting.scale.x
        else:
            maxNumModels = max(self.__numModelsPerEdgeState.values())
            size = self.__DEFAULT_DASH_SIZE
            color = self.__DEFAULT_DASH_COLOR
            gap = (self.__length - maxNumModels * size[0]) / maxNumModels
            length = size[0]
        shift = gap + length
        offset = (self.__length - shift) * Vector3(-0.5, 0, 0)
        return DashesParams(size, color, shift, offset)
