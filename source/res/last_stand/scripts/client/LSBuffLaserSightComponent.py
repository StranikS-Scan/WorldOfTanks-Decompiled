# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSBuffLaserSightComponent.py
import BigWorld
import Math
import logging
from gui.shared.utils.graphics import isRendererPipelineDeferred
from dyn_components_groups import groupComponent
from script_component.DynamicScriptComponent import DynamicScriptComponent
from xml_config_specs import StrParam, FloatParam
from vehicle_systems.stricted_loading import makeCallbackWeak
from helpers.CallbackDelayer import CallbackDelayer
from constants import CollisionFlags
_logger = logging.getLogger(__name__)

@groupComponent(beamModel=StrParam(), beamModelFwd=StrParam(), bindNode=StrParam(), modelLength=FloatParam(), sightMaxDistance=FloatParam())
class LSBuffLaserSightComponent(DynamicScriptComponent):
    UPDATE_RATE = 0.1

    def __init__(self):
        super(LSBuffLaserSightComponent, self).__init__()
        self._beamModelPath = None
        self._beamModel = None
        self._beamMP = None
        self._bindNode = None
        self._taskID = None
        self._callbackDelayer = CallbackDelayer()
        self._modelLength = self.groupComponentConfig.modelLength
        self._sightMaxDistance = self.groupComponentConfig.sightMaxDistance
        return

    def onDestroy(self):
        if self._beamModel is not None and self._beamModel.attached:
            BigWorld.player().delModel(self._beamModel)
        self._callbackDelayer.destroy()
        if self._taskID is not None:
            BigWorld.stopLoadResourceListBGTask(self._taskID)
        self._beamModelPath = None
        self._beamModel = None
        self._beamMP = None
        self._bindNode = None
        self._taskID = None
        self._callbackDelayer = None
        super(LSBuffLaserSightComponent, self).onDestroy()
        return

    def _onAvatarReady(self):
        super(LSBuffLaserSightComponent, self)._onAvatarReady()
        self._beamModelPath = self.groupComponentConfig.beamModel if isRendererPipelineDeferred() else self.groupComponentConfig.beamModelFwd
        resources = (self._beamModelPath,)
        self._taskID = BigWorld.loadResourceListBG(resources, makeCallbackWeak(self._onLoaded))

    def _onLoaded(self, resourceRefs):
        if self._taskID is None or self.entity.isDestroyed or self.entity.model is None or not self.entity.isAlive():
            return
        else:
            self._taskID = None
            if self._beamModelPath in resourceRefs.failedIDs:
                logging.error('Failed to load laser beam model: %s.', self._beamModelPath)
                return
            self._beamModel = resourceRefs[self._beamModelPath]
            self._bindNode = self.entity.model.node(self.groupComponentConfig.bindNode)
            if self._bindNode is None:
                logging.error('Failed to find bind node: %s.', self._bindNode)
                return
            scaleMatrix = Math.Matrix()
            scaleMatrix.setIdentity()
            self._beamMP = Math.MatrixProduct()
            self._beamMP.a = scaleMatrix
            self._beamMP.b = self._bindNode
            self._beamModel.addMotor(BigWorld.Servo(self._beamMP))
            BigWorld.player().addModel(self._beamModel)
            self._callbackDelayer.delayCallback(self.UPDATE_RATE, self._updateLaserPoint)
            return

    def _updateLaserPoint(self):
        gunMat = Math.Matrix(self._bindNode)
        gunPos = gunMat.translation
        gunDir = gunMat.applyVector((0, 0, 1))
        endPos = gunPos + gunDir * self._sightMaxDistance
        collidePos = BigWorld.wg_collideDynamicStatic(self.entity.spaceID, gunPos, endPos, CollisionFlags.TRIANGLE_PROJECTILENOCOLLIDE, self.entity.id, -1, 0)
        if collidePos:
            endPos = collidePos[0]
        self._beamMP.a.setScale((1, 1, gunPos.distTo(endPos) / self._modelLength))
        return self.UPDATE_RATE
