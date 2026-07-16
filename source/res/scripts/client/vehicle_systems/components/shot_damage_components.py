# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/shot_damage_components.py
import CGF
import Math
import BigWorld
from items import vehicles
from vehicle_systems.tankStructure import TankPartNames
from cgf_script.registration import ComponentProperty, registerComponent

class ShotDamageComponent(object):

    def __init__(self, partName, compound):
        self.partName = partName
        self.compound = compound


@registerComponent
class DamageStickerComponent(object):
    category = 'Render'
    editorTitle = 'Damage Sticker Component'
    domain = CGF.Domain.Client
    damageSticker = ComponentProperty(type=CGF.PropertyType.String, editorName='Damage sticker', value='')
    lodDistance = ComponentProperty(type=CGF.PropertyType.Float, editorName='Lod Distance', value=100)
    fadeoutTime = ComponentProperty(type=CGF.PropertyType.Float, editorName='Fadeout time', value=0)
    offset = ComponentProperty(type=CGF.PropertyType.Float, editorName='Offset', value=1.0)

    def __init__(self):
        super(DamageStickerComponent, self).__init__()
        self.stickerModel = None
        return


class DamageStickerSystem(CGF.System):
    StickerActivated = CGF.ActivateReaction(CGF.ReactRw(ShotDamageComponent), CGF.ReactRw(DamageStickerComponent), CGF.Ro(CGF.TransformComponent))
    StickerDeaactivated = CGF.DeactivateReaction(CGF.ReactRw(ShotDamageComponent), CGF.ReactRw(DamageStickerComponent))
    Reactions = CGF.Reactions(StickerActivated, StickerDeaactivated)

    def update(self):
        for damage, sticker in self.reaction(self.StickerDeaactivated):
            if sticker.stickerModel is None:
                continue
            node = damage.compound.node(TankPartNames.getActualNodeNameByPartName(damage.partName))
            node.detach(sticker.stickerModel)

        for damage, sticker, tr in self.reaction(self.StickerActivated):
            if damage.partName == TankPartNames.CHASSIS:
                continue
            sticker.stickerModel = BigWorld.WGStickerModel(self.spaceID)
            geometryLink = damage.compound.getPartGeometryLink(TankPartNames.getIdx(damage.partName))
            m = Math.Matrix()
            m.setIdentity()
            stickerModel = sticker.stickerModel
            stickerModel.setupSuperModel(geometryLink, m)
            node = damage.compound.node(TankPartNames.getActualNodeNameByPartName(damage.partName))
            node.attach(sticker.stickerModel)
            stickerModel.setLODDistance(sticker.lodDistance)
            stickerId = vehicles.g_cache.damageStickers['ids'][sticker.damageSticker]
            segStart = tr.transform.applyPoint(Math.Vector3(0, 0, -sticker.offset))
            segEnd = tr.transform.applyPoint(Math.Vector3(0, 0, sticker.offset))
            stickerModel.addDamageSticker(stickerId, segStart, segEnd, True)
            stickerModel.setupFadeout(sticker.fadeoutTime)

        return
