# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientSelectableCameraVehicle.py
import Math
import BigWorld
from ClientSelectableCameraObject import ClientSelectableCameraObject
from gui.hangar_vehicle_appearance import HangarVehicleAppearance
from vehicle_systems.tankStructure import ModelStates
from vehicle_systems.tankStructure import TankPartIndexes
from gui.ClientHangarSpace import hangarCFG
from gui.shared.utils.HangarSpace import g_hangarSpace

class ClientSelectableCameraVehicle(ClientSelectableCameraObject):
    appearance = property(lambda self: self.__vAppearance)

    def __init__(self):
        ClientSelectableCameraObject.__init__(self)
        self.__vAppearance = None
        self.typeDescriptor = None
        self.__onLoadedCallback = None
        self.__fakeShadowModel = None
        self.__shadowModelFashion = None
        self.__isVehicleLoaded = False
        return

    def onEnterWorld(self, prereqs):
        super(ClientSelectableCameraVehicle, self).onEnterWorld(prereqs)
        if self.__vAppearance is None:
            self.__vAppearance = HangarVehicleAppearance(self.spaceID, self)
            self.recreateVehicle(None, ModelStates.UNDAMAGED, lambda : None)
        g_hangarSpace.onSpaceCreate += self._onSpaceCreated
        return

    def _onSpaceCreated(self):
        self.__createFakeShadow()

    def onLeaveWorld(self):
        g_hangarSpace.onSpaceCreate -= self._onSpaceCreated
        if self.__vAppearance:
            self.__vAppearance.destroy()
            self.__vAppearance = None
        self.typeDescriptor = None
        self.__shadowModelFashion = None
        if self.__fakeShadowModel:
            BigWorld.delModel(self.__fakeShadowModel)
            self.__fakeShadowModel = None
        super(ClientSelectableCameraVehicle, self).onLeaveWorld()
        return

    def prerequisites(self):
        return []

    def recreateVehicle(self, typeDescriptor=None, state=ModelStates.UNDAMAGED, callback=None):
        if typeDescriptor is not None:
            self.typeDescriptor = typeDescriptor
        self.__onLoadedCallback = callback
        if self.typeDescriptor is not None and self.__vAppearance is not None:
            self.__vAppearance.recreate(self.typeDescriptor, state, self._onVehicleLoaded)
        self.__updateFakeShadowAccordingToAppearance()
        return

    def _onVehicleLoaded(self):
        self.__updateFakeShadowAccordingToAppearance()
        if self.__onLoadedCallback is not None:
            self.__onLoadedCallback()
            self.__onLoadedCallback = None
        self.__isVehicleLoaded = True
        return

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
        return self.__isVehicleLoaded

    def _getMovingSound(self):
        return None

    def _getNextMusicState(self):
        return None

    def setSelectable(self, flag):
        if flag:
            self.targetCaps = []
        else:
            self.targetCaps = [0]

    def __createFakeShadow(self):
        cfg = hangarCFG()
        shadowName = cfg.get('shadow_model_name', None)
        if shadowName and not self.__fakeShadowModel:
            self.__shadowModelFashion = BigWorld.WGTextureFashion()
            self.__fakeShadowModel = BigWorld.Model(shadowName)
            BigWorld.addModel(self.__fakeShadowModel)
            shadowModelYOffset = cfg['shadow_forward_y_offset'] if BigWorld.getGraphicsSetting('RENDER_PIPELINE') == 1 else cfg['shadow_deferred_y_offset']
            self.__fakeShadowModel.position = Math.Vector3(self.position.x, self.position.y + shadowModelYOffset, self.position.z)
            self.__fakeShadowModel.yaw = self.yaw
            self.__fakeShadowModel.fashion = self.__shadowModelFashion
        self.__updateFakeShadowAccordingToAppearance()
        return

    def __updateFakeShadowAccordingToAppearance(self):
        if not self.__shadowModelFashion:
            return
        cfg = hangarCFG()
        if self.__vAppearance and self.__vAppearance.isLoaded():
            appearanceTexture = self.__vAppearance.fakeShadowDefinedInHullTexture
            shadowMapTexFileName = appearanceTexture if appearanceTexture else cfg['shadow_default_texture_name']
        else:
            shadowMapTexFileName = cfg['shadow_empty_texture_name']
        if shadowMapTexFileName:
            self.__shadowModelFashion.setTexture(shadowMapTexFileName, 'diffuseMap')
