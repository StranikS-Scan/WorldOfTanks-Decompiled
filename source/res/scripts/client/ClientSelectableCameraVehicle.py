# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableCameraVehicle.py
from collections import namedtuple
import Math
import BigWorld
from ClientSelectableCameraObject import ClientSelectableCameraObject
from gui.hangar_vehicle_appearance import HangarVehicleAppearance
from items.vehicles import stripOptionalDeviceFromVehicleCompactDescr
from vehicle_systems.tankStructure import ModelStates
from vehicle_systems.tankStructure import TankPartIndexes
from gui.ClientHangarSpace import hangarCFG
from EdgeDrawer import HighlightComponent
_VehicleTransformParams = namedtuple('_VehicleTransformParams', ('targetPos', 'rotateYPR', 'shadowModelYOffset'))

class ClientSelectableCameraVehicle(ClientSelectableCameraObject):
    appearance = property(lambda self: self.__vAppearance)

    def __init__(self):
        ClientSelectableCameraObject.__init__(self)
        self.__vAppearance = None
        self.typeDescriptor = None
        self.__onLoadedCallback = None
        self.__fakeShadowModel = None
        self.__shadowModelFashion = None
        self._isVehicleLoaded = False
        self.__vehicleTransform = None
        self.__defaultPos = Math.Vector3(0, 0, 0)
        self.__defaultYPR = Math.Vector3(0, 0, 0)
        return

    def prerequisites(self):
        cfg = hangarCFG()
        if 'shadow_model_name' in cfg:
            modelNames = (cfg['shadow_model_name'],)
            return modelNames

    def onEnterWorld(self, prereqs):
        super(ClientSelectableCameraVehicle, self).onEnterWorld(prereqs)
        self.__defaultPos = self.position
        self.__defaultYPR = Math.Vector3(self.yaw, self.pitch, self.roll)
        cfg = hangarCFG()
        if 'shadow_model_name' in cfg:
            shadowName = cfg['shadow_model_name']
            if shadowName not in prereqs.failedIDs:
                self.__createFakeShadow(prereqs[shadowName])

    def onLeaveWorld(self):
        super(ClientSelectableCameraVehicle, self).onLeaveWorld()
        if self.__vAppearance:
            self.__vAppearance.destroy()
            self.__vAppearance = None
        self.typeDescriptor = None
        self.__shadowModelFashion = None
        if self.__fakeShadowModel is not None and self.__fakeShadowModel in BigWorld.models():
            BigWorld.delModel(self.__fakeShadowModel)
            self.__fakeShadowModel.fashion = None
            self.__fakeShadowModel = None
        return

    def recreateVehicle(self, typeDescriptor=None, state=ModelStates.UNDAMAGED, callback=None, outfit=None):
        self._isVehicleLoaded = False
        self.setHighlight(False)
        if typeDescriptor is not None:
            self.typeDescriptor = typeDescriptor
        self.__onLoadedCallback = callback
        if self.typeDescriptor is not None:
            self._isVehicleLoaded = False
            if self.__vAppearance is None:
                self.__vAppearance = self._createAppearance()
            self.__vAppearance.recreate(self.typeDescriptor, state, self._onVehicleLoaded, outfit)
        self.__updateFakeShadowAccordingToAppearance()
        return

    def removeVehicle(self):
        self.setHighlight(False)
        self._isVehicleLoaded = False
        if self.__vAppearance:
            self.__vAppearance.remove()
        self.__updateFakeShadowAccordingToAppearance()

    def updateVehicleCustomization(self, outfit):
        recreate = self.appearance.recreateRequired(outfit)
        if recreate:
            self._isVehicleLoaded = False
            self.appearance.recreate(self.typeDescriptor, callback=self._onVehicleLoaded, outfit=outfit)
        else:
            self.appearance.updateCustomization(outfit, self._onVehicleRefreshed)

    def updateVehicleDescriptor(self, descr):
        if descr is None:
            return
        else:
            if self.__descriptorRequiresRecreate(descr):
                self._isVehicleLoaded = False
                self.typeDescriptor = descr
                if self.__vAppearance is None:
                    self.__vAppearance = self._createAppearance()
                self.__vAppearance.recreate(self.typeDescriptor, callback=self._onVehicleLoaded)
            else:
                self.typeDescriptor = descr
            return

    def _createAppearance(self):
        return HangarVehicleAppearance(self.spaceID, self)

    def _onVehicleLoaded(self):
        self.__updateFakeShadowAccordingToAppearance()
        self._isVehicleLoaded = True
        if self.__onLoadedCallback is not None:
            self.__onLoadedCallback()
            self.__onLoadedCallback = None
        self.__restoreTransform()
        return

    def _onVehicleRefreshed(self):
        self.__restoreTransform()

    def _getModelHeight(self):
        boundsTurret = Math.Matrix(self.model.getBoundsForPart(TankPartIndexes.TURRET))
        boundsChassis = Math.Matrix(self.model.getBoundsForPart(TankPartIndexes.CHASSIS))
        minY = boundsChassis.translation.y
        maxY = boundsTurret.translation.y + boundsTurret.get(1, 1)
        return maxY - minY

    def getModelLength(self):
        return self.__vAppearance.computeVehicleLength() if self.__vAppearance else 0

    @property
    def isVehicleLoaded(self):
        return self._isVehicleLoaded

    def setSelectable(self, flag):
        if flag:
            self.targetCaps = []
        else:
            self.targetCaps = [0]

    def _setVehicleModelTransform(self, targetPos, rotateYPR, shadowModelYOffset=None):
        self.__vehicleTransform = _VehicleTransformParams(targetPos, rotateYPR, shadowModelYOffset)
        m = Math.Matrix()
        m.setRotateYPR(rotateYPR)
        m.translation = Math.Vector3(targetPos)
        self.model.matrix = m
        self.teleport(targetPos, rotateYPR)
        self.__setFakeShadowModelTransform(targetPos, rotateYPR, shadowModelYOffset)

    def _resetVehicleModelTransform(self):
        self.__vehicleTransform = None
        self.teleport(self.__defaultPos, self.__defaultYPR)
        self.__setFakeShadowModelTransform(self.__defaultPos, self.__defaultYPR)
        return

    def _addEdgeDetect(self):
        if self.__isHighlightable():
            super(ClientSelectableCameraVehicle, self)._addEdgeDetect()
            go = self.__vAppearance.gameObject
            go.createComponent(HighlightComponent, 0, self.edgeMode, False, False)

    def _delEdgeDetect(self):
        if self.__isHighlightable():
            super(ClientSelectableCameraVehicle, self)._delEdgeDetect()
            go = self.__vAppearance.gameObject
            go.removeComponentByType(HighlightComponent)

    def __isHighlightable(self):
        return self.__vAppearance is not None and not self.__vAppearance.isVehicleDestroyed

    def __createFakeShadow(self, model):
        if self.__fakeShadowModel is None:
            self.__fakeShadowModel = model
            self.__shadowModelFashion = BigWorld.WGTextureFashion()
            BigWorld.addModel(self.__fakeShadowModel, self.spaceID)
            self.__fakeShadowModel.fashion = self.__shadowModelFashion
        self.__updateFakeShadowAccordingToAppearance()
        return

    def __updateFakeShadowAccordingToAppearance(self):
        if self.__shadowModelFashion is None or self.__fakeShadowModel is None:
            return
        else:
            cfg = hangarCFG()
            if self.__vAppearance is not None and self.__vAppearance.isLoaded():
                appearanceTexture = self.__vAppearance.fakeShadowDefinedInHullTexture
                shadowMapTexFileName = appearanceTexture if appearanceTexture else cfg['shadow_default_texture_name']
            else:
                shadowMapTexFileName = cfg['shadow_empty_texture_name']
            if shadowMapTexFileName:
                self.__shadowModelFashion.setTexture(shadowMapTexFileName, 'diffuseMap')
            self.__setFakeShadowModelTransform(self.position)
            return

    def __setFakeShadowModelTransform(self, position, rotateYPR=None, shadowModelYOffset=None):
        if self.__fakeShadowModel is None:
            return
        else:
            if shadowModelYOffset is None:
                cfg = hangarCFG()
                shadowModelYOffset = cfg['shadow_forward_y_offset'] if BigWorld.getGraphicsSetting('RENDER_PIPELINE') == 1 else cfg['shadow_deferred_y_offset']
            if rotateYPR is None:
                rotateYPR = Math.Vector3(self.yaw, self.pitch, self.roll)
            result = Math.Matrix()
            result.setTranslate(Math.Vector3(0, shadowModelYOffset, 0))
            rotation = Math.Matrix()
            rotation.setRotateYPR(rotateYPR)
            translation = Math.Matrix()
            translation.setTranslate(position)
            result.postMultiply(rotation)
            result.postMultiply(translation)
            self.__fakeShadowModel.worldTransform = result
            return

    def __restoreTransform(self):
        if self.__vehicleTransform is None:
            return
        else:
            self._setVehicleModelTransform(self.__vehicleTransform.targetPos, self.__vehicleTransform.rotateYPR, self.__vehicleTransform.shadowModelYOffset)
            return

    def __descriptorRequiresRecreate(self, desc):
        if self.typeDescriptor is None:
            return True
        else:
            oldDescriptor = stripOptionalDeviceFromVehicleCompactDescr(self.typeDescriptor.makeCompactDescr())
            newDescriptor = stripOptionalDeviceFromVehicleCompactDescr(desc.makeCompactDescr())
            return True if oldDescriptor != newDescriptor else False
