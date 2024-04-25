# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/terrain_circle_component.py
import logging
import math
import typing
from collections import namedtuple
import BigWorld
from Math import Vector2
from items import _xml
from helpers.CallbackDelayer import CallbackDelayer
from gui.battle_control.matrix_factory import makeVehicleEntityMP
if typing.TYPE_CHECKING:
    from BigWorld import PyTerrainSelectedArea
g_logger = logging.getLogger(__name__)
MIN_OVER_TERRAIN_HEIGHT = 0
MIN_UPDATE_INTERVAL = 0
TerrainCircleSettings = namedtuple('TerrainCircleSettings', ('modelPath', 'color', 'enableAccurateCollision', 'maxUpdateInterval', 'overTerrainHeight', 'cutOffYDistance'))

def readTerrainCircleSettings(xmlSection, xmlCtx, xmlTag):
    settings = xmlSection[xmlTag]
    return TerrainCircleSettings(modelPath=_xml.readString(xmlCtx, settings, 'visual'), color=int(_xml.readString(xmlCtx, settings, 'color'), 0), enableAccurateCollision=_xml.readBool(xmlCtx, settings, 'enableAccurateCollision'), maxUpdateInterval=max(MIN_UPDATE_INTERVAL, _xml.readFloat(xmlCtx, settings, 'maxUpdateInterval')), overTerrainHeight=max(MIN_OVER_TERRAIN_HEIGHT, _xml.readFloat(xmlCtx, settings, 'overTerrainHeight')), cutOffYDistance=_xml.readFloat(xmlCtx, settings, 'cutOffYDistance', -1.0))


class TerrainCircleComponent(CallbackDelayer):
    CUT_OFF_ANGLE = math.radians(60)

    def __init__(self):
        super(TerrainCircleComponent, self).__init__()
        self.__maxUpdateInterval = 0.04
        self.__areaVisual = None
        self.__motor = None
        self.__model = None
        self.__vehicleID = None
        self.__isVisible = False
        return

    def configure(self, radius, terrainCircleSettings):
        if self.__areaVisual is None:
            self.__create()
        terrainColor = terrainCircleSettings.color
        if terrainColor == 0:
            g_logger.warning('The color of Terrain Circle is 0! Terrain circle will be invisible!')
        self.__maxUpdateInterval = terrainCircleSettings.maxUpdateInterval
        visual = self.__areaVisual
        visual.setup(terrainCircleSettings.modelPath, Vector2(radius + radius, radius + radius), terrainCircleSettings.overTerrainHeight, terrainColor)
        visual.enableAccurateCollision(terrainCircleSettings.enableAccurateCollision)
        visual.enableWaterCollision(terrainCircleSettings.enableWaterCollision)
        if self.__isVisible:
            self.__update()
        enableYCutOff = False
        if terrainCircleSettings.cutOffDistance is not None:
            visual.setCutOffDistance(terrainCircleSettings.cutOffDistance)
            visual.setCutOffAngle(self.CUT_OFF_ANGLE)
            enableYCutOff = True
        if terrainCircleSettings.cutOffAngle is not None:
            visual.setCutOffAngle(math.radians(terrainCircleSettings.cutOffAngle))
            enableYCutOff = True
        if enableYCutOff:
            visual.enableYCutOff(True)
        if terrainCircleSettings.minHeight is not None:
            visual.setMinHeight(terrainCircleSettings.minHeight)
        if terrainCircleSettings.maxHeight is not None:
            visual.setMaxHeight(terrainCircleSettings.maxHeight)
        return

    def destroy(self):
        if self.__vehicleID is not None:
            g_logger.error('destroy called when still attached.')
            self.detach()
        if self.__model is not None and self.__model.node('').inWorld:
            BigWorld.player().delModel(self.__model)
        self.__model = None
        self.__areaVisual = None
        self.__vehicleID = None
        self.__motor = None
        CallbackDelayer.destroy(self)
        return

    def isVisible(self):
        return self.__vehicleID is not None and self.__isVisible

    def isAttached(self):
        return self.__vehicleID is not None

    def setVisible(self, visible=True):
        if self.__vehicleID is None:
            self.__isVisible = visible
            g_logger.warning('setVisible: TerrainCircleComponent is not attached.')
            return
        else:
            if visible != self.__isVisible:
                self.stopCallback(self.__update)
                self.__isVisible = visible
                if visible:
                    self.__attachAreaVisualToModel()
                    self.__update()
                else:
                    self.__detachAreaVisualFromModel()
            return

    def attach(self, vehicleID):
        if self.__areaVisual is None:
            g_logger.error('attach: TerrainCircleComponent is not yet created. Call configure first.')
            return
        elif self.__vehicleID is not None:
            g_logger.error('attach: TerrainCircleComponent is already attached. Needs to be detached first.')
            return
        else:
            self.__vehicleID = vehicleID
            if self.__isVisible:
                self.__attachAreaVisualToModel()
            self.__setMotor()
            return

    def detach(self):
        if self.__vehicleID is None:
            g_logger.error('detach: TerrainCircleComponent is not attached to anything.')
            return
        else:
            if self.__isVisible:
                self.__detachAreaVisualFromModel()
            self.__removeMotor()
            self.__vehicleID = None
            return

    def __attachAreaVisualToModel(self):
        node = self.__model.node('')
        if node is not None:
            node.attach(self.__areaVisual)
        else:
            g_logger.error('__attachAreaVisualToModel: Failed to attach: no area visual or attachment node not found.')
        return

    def __detachAreaVisualFromModel(self):
        node = self.__model.node('')
        if self.__areaVisual and node:
            node.detach(self.__areaVisual)
        else:
            g_logger.error('__detachAreaVisualFromModel: Failed to detach: no area visual or attachment node not found.')

    def __setMotor(self):
        vehicle = BigWorld.entity(self.__vehicleID)
        self.__motor = BigWorld.Servo(makeVehicleEntityMP(vehicle))
        self.__model.addMotor(self.__motor)

    def __removeMotor(self):
        self.__model.delMotor(self.__motor)
        self.__motor = None
        return

    def __create(self):
        self.__areaVisual = BigWorld.PyTerrainSelectedArea()
        self.__model = BigWorld.Model('')
        BigWorld.player().addModel(self.__model)

    def __update(self):
        if self.__isVisible:
            self.__areaVisual.updateHeights()
            self.delayCallback(self.__getUpdateInterval(), self.__update)

    def __getUpdateInterval(self):
        smoothFPS = BigWorld.getFPS()[1]
        if smoothFPS == 0:
            smoothFPS = 1
        return max(1 / smoothFPS, self.__maxUpdateInterval)
