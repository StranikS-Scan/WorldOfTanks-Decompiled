# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/shot_damage_components.py
from cgf_script.component_meta_class import CGFComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
import CGF
import Math
import BigWorld
import GenericComponents
from items import vehicles
from vehicle_systems.tankStructure import TankPartNames

class ShotDamageComponent(object):

    def __init__(self, partName, compound):
        self.partName = partName
        self.compound = compound


class DamageStickerComponent(CGFComponent):
    category = 'Render'
    damageSticker = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Damage sticker', value='')
    lodDistance = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Lod Distance', value=100)
    fadeoutTime = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Fadeout time', value=0)
    offset = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Offset', value=1.0)

    def __init__(self):
        super(DamageStickerComponent, self).__init__()
        self.stickerModel = BigWorld.WGStickerModel()


@autoregister(presentInAllWorlds=True)
class DamageStickerManager(CGF.ComponentManager):

    @onAddedQuery(ShotDamageComponent, DamageStickerComponent, GenericComponents.TransformComponent)
    def onAddedSticker(self, shotDamage, damageSticker, transform):
        geometryLink = shotDamage.compound.getPartGeometryLink(TankPartNames.getIdx(shotDamage.partName))
        m = Math.Matrix()
        m.setIdentity()
        stickerModel = damageSticker.stickerModel
        stickerModel.setupSuperModel(geometryLink, m)
        node = shotDamage.compound.node(shotDamage.partName)
        node.attach(damageSticker.stickerModel)
        stickerModel.setLODDistance(damageSticker.lodDistance)
        stickerId = vehicles.g_cache.damageStickers['ids'][damageSticker.damageSticker]
        segStart = transform.transform.applyPoint(Math.Vector3(0, 0, -damageSticker.offset))
        segEnd = transform.transform.applyPoint(Math.Vector3(0, 0, damageSticker.offset))
        stickerModel.addDamageSticker(stickerId, segStart, segEnd, True)
        stickerModel.setupFadeout(damageSticker.fadeoutTime)

    @onRemovedQuery(ShotDamageComponent, DamageStickerComponent)
    def onRemovedSticker(self, shotDamage, damageSticker):
        node = shotDamage.compound.node(shotDamage.partName)
        node.detach(damageSticker.stickerModel)
