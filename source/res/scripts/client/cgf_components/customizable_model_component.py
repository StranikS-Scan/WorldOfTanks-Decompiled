# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/customizable_model_component.py
import CGF
import BigWorld
import GenericComponents
import Vehicular
import Math
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery, autoregister
from helpers import isPlayerAvatar
from vehicle_systems.tankStructure import TankPartNames, TankPartIndexes
from vehicle_systems import camouflages
from debug_utils import LOG_ERROR
from constants import IS_UE_EDITOR

@registerComponent
class CustomizableModelAttachmentComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Customizable model attachment'
    category = 'Render'
    tankPart = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Tank part', value=TankPartNames.HULL, annotations={'comboBox': {TankPartNames.HULL: TankPartNames.HULL,
                  TankPartNames.TURRET: TankPartNames.TURRET,
                  TankPartNames.GUN: TankPartNames.GUN}})
    enablePaint = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Enable paint', value=True)
    enableCamouflage = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Enable camouflage', value=True)
    enableDecals = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Enable decals', value=True)
    enableDirt = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='Enable dirt', value=True)


class ModelFashionAttachedComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor

    def __init__(self, appearanceId):
        self.appearanceId = appearanceId


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor)
class CustomizableModelManager(CGF.ComponentManager):

    def __init__(self):
        super(CustomizableModelManager, self).__init__()
        self.__fashions = {}
        self.__dirtComponents = {}
        self.__tempFashionModifiers = {}

    def deactivate(self):
        self.clear()

    def destroy(self):
        self.clear()

    def clear(self):
        self.__fashions = {}
        self.__dirtComponents = {}
        self.__tempFashionModifiers = {}

    @onAddedQuery(CustomizableModelAttachmentComponent, GenericComponents.DynamicModelComponent, CGF.No(ModelFashionAttachedComponent), CGF.GameObject, tickGroup='postHierarchyUpdateFinish')
    def onAddedModel(self, _, modelComponent, go):
        self.__fashions[go.id] = BigWorld.WGBaseFashion()
        self.updateAttachmentFashions(go)

    @onAddedQuery(CGF.GameObject, GenericComponents.DynamicModelComponent, ModelFashionAttachedComponent)
    def onAddedModelFashion(self, go, modelComponent, _):
        fashion = self.__fashions.get(go.id)
        if fashion:
            modelComponent.setPartFashion(0, self.__fashions[go.id])

    def updateOutfit(self, appearanceId, outfit):
        self.__tempFashionModifiers[appearanceId] = outfit

    def clearTempOutfit(self, appearanceId):
        if appearanceId in self.__tempFashionModifiers:
            del self.__tempFashionModifiers[appearanceId]

    def __applyCamo(self, c11nComponent, camo):
        c11nComponent.setPartCamo(camo)

    def __applyPaint(self, c11Component, repaint):
        c11Component.setPartPaint(repaint)

    def __applyDecals(self, c11Component, decals):
        c11Component.setDecals(decals)

    def updateDirtComponents(self, appearanceId, *args):
        if appearanceId not in self.__dirtComponents:
            return
        for dirtComponent in self.__dirtComponents[appearanceId].values():
            dirtComponent.update(*args)

    def updateAttachmentFashions(self, gameObject):
        hManager = CGF.HierarchyManager(gameObject.spaceID)
        root = hManager.getTopMostParent(gameObject)
        if not IS_UE_EDITOR:
            entityComponent = root.findComponentByType(GenericComponents.EntityGOSync)
            if not entityComponent:
                LOG_ERROR("CustomizableModelManager: couldn't find root entity")
                return
            if gameObject.findComponentByType(ModelFashionAttachedComponent):
                LOG_ERROR('CustomizableModelManager: attachment customization is already installed!')
                return
            appearanceContainer = entityComponent.entity
        else:
            from common_tank_appearance import VehicleAppearanceComponent
            appearanceContainer = root.findComponentByType(VehicleAppearanceComponent)
        if not appearanceContainer:
            LOG_ERROR("CustomizableModelManager: can't find appearance component")
            return
        appearance = appearanceContainer.appearance
        vDesc = appearance.typeDescriptor if hasattr(appearance, 'typeDescriptor') else appearanceContainer.typeDescriptor
        outfit = appearance.outfit
        damagedState = hasattr(appearance, 'isVehicleDestroyed') and appearance.isVehicleDestroyed or hasattr(appearance, 'damageState') and appearance.damageState.isCurrentModelDamaged
        attachmentModelComponent = gameObject.findComponentByType(CustomizableModelAttachmentComponent)
        if not attachmentModelComponent:
            return
        camos, paints, decals, materials = camouflages.getOutfitData(appearance, outfit, vDesc, damagedState)
        tankPartIdx = TankPartNames.getIdx(attachmentModelComponent.tankPart)
        newCamos = [camos[tankPartIdx]] if attachmentModelComponent.enableCamouflage else []
        newPaints = [paints[tankPartIdx]] if attachmentModelComponent.enablePaint else []
        newDecals = decals if attachmentModelComponent.enableDecals else []
        newOutfitData = (newCamos,
         newPaints,
         newDecals,
         materials)
        referenceGO = gameObject
        localTransform = Math.Matrix()
        while referenceGO.id != root.id:
            currentTransformComponent = referenceGO.findComponentByType(GenericComponents.TransformComponent)
            if currentTransformComponent:
                localTransform.postMultiply(currentTransformComponent.transform)
            referenceGO = referenceGO.findComponentByType(GenericComponents.HierarchyComponent).parent
            if not referenceGO:
                break

        if not IS_UE_EDITOR and not isPlayerAvatar():
            c11nComponent = self.__createC11nComponent(gameObject, Vehicular.C11nAttachmentEditComponent, self.__fashions[gameObject.id], localTransform, newOutfitData)
            if appearance.id in self.__tempFashionModifiers:
                outfit = self.__tempFashionModifiers[appearance.id]
                if attachmentModelComponent.enableCamouflage:
                    camo = camouflages.getCamo(appearance, outfit, tankPartIdx, vDesc, TankPartIndexes.getName(tankPartIdx), damagedState)
                    self.__applyCamo(c11nComponent, camo)
                if attachmentModelComponent.enablePaint:
                    repaint = camouflages.getRepaint(outfit, tankPartIdx, vDesc)
                    self.__applyPaint(c11nComponent, repaint)
                if attachmentModelComponent.enableDecals:
                    decals = camouflages.getGenericProjectionDecals(outfit, vDesc)
                    c11nComponent.setDecals(decals)
        else:
            self.__createC11nComponent(gameObject, Vehicular.C11nAttachmentComponent, self.__fashions[gameObject.id], localTransform, newOutfitData)
        dirtEnabled = BigWorld.WG_dirtEnabled() and 'HD' in vDesc.type.tags and attachmentModelComponent.enableDirt
        if dirtEnabled:
            if gameObject.findComponentByType(Vehicular.DirtComponent):
                gameObject.removeComponentByType(Vehicular.DirtComponent)
            dirtHandlers = [BigWorld.PyDirtHandler(False, localTransform.translation.y)]
            modelHeight, _ = appearance.computeVehicleHeight()
            dirtComponent = gameObject.createComponent(Vehicular.DirtComponent, dirtHandlers, modelHeight)
            if appearance.id not in self.__dirtComponents:
                self.__dirtComponents[appearance.id] = {}
            self.__dirtComponents[appearance.id][gameObject.id] = dirtComponent
            self.__fashions[gameObject.id].addMaterialHandler(dirtHandlers[0])
            if IS_UE_EDITOR or isPlayerAvatar():
                self.__fashions[gameObject.id].addTrackMaterialHandler(dirtHandlers[0])
            else:
                dirtComponent.setBase()
        if not gameObject.findComponentByType(ModelFashionAttachedComponent):
            gameObject.createComponent(ModelFashionAttachedComponent, appearance.id)

    def __createC11nComponent(self, gameObject, componentType, fashion, localTransform, outfitData):
        c11nComponent = gameObject.findComponentByType(componentType)
        if c11nComponent:
            gameObject.removeComponentByType(componentType)
        c11nComponent = gameObject.createComponent(componentType, fashion, localTransform, outfitData)
        return c11nComponent
