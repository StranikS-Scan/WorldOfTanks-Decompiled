# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/inspire_area_visual.py
from collections import namedtuple
import BigWorld
import ResMgr
from debug_utils import LOG_ERROR
from items import _xml
from Math import Vector2
DYNAMIC_OBJECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'
AREA_VISUAL_TAG = 'InspireAreaVisual'
MIN_OVER_TERRAIN_HEIGHT = 0
MIN_UPDATE_INTERVAL = 0
InspireVisualSettings = namedtuple('InspireVisualSettings', ('modelPath', 'color', 'enableAccurateCollision', 'maxUpdateInterval', 'overTerrainHeight'))

def __readSettings():
    ctx = (None, DYNAMIC_OBJECTS_CONFIG_FILE + '/' + AREA_VISUAL_TAG)
    settings = ResMgr.openSection(DYNAMIC_OBJECTS_CONFIG_FILE)[AREA_VISUAL_TAG]
    return InspireVisualSettings(modelPath=_xml.readString(ctx, settings, 'visual'), color=int(_xml.readString(ctx, settings, 'color'), 0), enableAccurateCollision=_xml.readBool(ctx, settings, 'enableAccrurateCollision'), maxUpdateInterval=max(MIN_UPDATE_INTERVAL, _xml.readFloat(ctx, settings, 'maxUpdateInterval')), overTerrainHeight=max(MIN_OVER_TERRAIN_HEIGHT, _xml.readFloat(ctx, settings, 'overTerrainHeight')))


g_inspireVisualSettings = __readSettings()

class InspireAreaVisual(object):

    def __init__(self, radius):
        self.__areaVisual = visual = BigWorld.PyTerrainSelectedArea()
        visual.setup(g_inspireVisualSettings.modelPath, Vector2(radius + radius, radius + radius), g_inspireVisualSettings.overTerrainHeight, g_inspireVisualSettings.color)
        visual.enableAccurateCollision(g_inspireVisualSettings.enableAccurateCollision)
        self.__fakeModel = BigWorld.Model('')
        self.__fakeModel.node('').attach(self.__areaVisual)
        self.__callbackID = None
        return

    def setMotor(self, motor):
        if self.__fakeModel is None:
            LOG_ERROR("Property 'motor' accessed after object has been destroyed")
            return
        else:
            if self.__fakeModel.motors:
                self.__fakeModel.delMotor(self.__fakeModel.motors[0])
            self.__fakeModel.motors = ()
            self.__fakeModel.addMotor(motor)
            return

    def isVisible(self):
        if self.__fakeModel is None:
            LOG_ERROR("Property 'visible' accessed after object has been destroyed")
            return False
        else:
            return self.__fakeModel.node('').inWorld

    def setVisible(self, isVisible):
        if self.__fakeModel is None:
            LOG_ERROR("Property 'visible' accessed after object has been destroyed")
            return
        else:
            if isVisible != self.__fakeModel.node('').inWorld:
                if isVisible:
                    BigWorld.addModel(self.__fakeModel)
                    if self.__callbackID is not None:
                        BigWorld.cancelCallback(self.__callbackID)
                    self.__update()
                else:
                    BigWorld.delModel(self.__fakeModel)
                    if self.__callbackID is not None:
                        BigWorld.cancelCallback(self.__callbackID)
                        self.__callbackID = None
            return

    def __update(self):
        self.__areaVisual.updateHeights()
        self.__callbackID = BigWorld.callback(self.__getUpdateInterval(), self.__update)

    def destroy(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        if self.__fakeModel:
            node = self.__fakeModel.node('')
            if self.__areaVisual:
                node.detach(self.__areaVisual)
            self.__fakeModel.motors = ()
            if node.inWorld:
                BigWorld.delModel(self.__fakeModel)
        self.__areaVisual = None
        self.__fakeModel = None
        return

    def __getUpdateInterval(self):
        smoothFPS = BigWorld.getFPS()[1]
        if smoothFPS == 0:
            smoothFPS = 1
        return max(1 / smoothFPS, g_inspireVisualSettings.maxUpdateInterval)
