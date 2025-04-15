# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/common/story_mode_common/items/sm_artefacts.py
import typing
from items.artefacts import Equipment, AreaOfEffectEquipment, TooltipConfigReader, ArcadeEquipmentConfigReader, AreaMarkerConfigReader
from items import _xml
if typing.TYPE_CHECKING:
    from ResMgr import DataSection
    from Math import Vector3

class SPGZoneEquipment(AreaOfEffectEquipment):
    __slots__ = ('yawHitPrediction', 'hitPredictionDuration')

    def _readConfig(self, xmlCtx, section):
        super(SPGZoneEquipment, self)._readConfig(xmlCtx, section)
        self.yawHitPrediction = section.readInt('yawHitPrediction', 0)
        self.hitPredictionDuration = section.readFloat('hitPredictionDuration', 0)


class BaseAbilityEquipment(Equipment, TooltipConfigReader, ArcadeEquipmentConfigReader, AreaMarkerConfigReader):
    __slots__ = ('navmeshGirth', 'heightAboveBase', 'prepareTime', 'respawnTime', 'cooldownTime', 'unspotDelay', 'navmeshGirth', 'directVisionRadius', 'visionMinRadius', 'detectFromVehicle', 'observationPoints') + TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS + AreaMarkerConfigReader._MARKER_SLOTS_

    def __init__(self):
        super(BaseAbilityEquipment, self).__init__()
        self.initTooltipInformation()
        self.initArcadeInformation()
        self.initMarkerInformation()

    def _readConfig(self, xmlCtx, section):
        super(BaseAbilityEquipment, self)._readConfig(xmlCtx, section)
        self.readTooltipInformation(xmlCtx, section)
        self.readArcadeInformation(xmlCtx, section)
        self.readMarkerConfig(xmlCtx, section)
        self.navmeshGirth = section.readString('navmeshGirth')
        self.prepareTime = section.readFloat('prepareTime')
        self.respawnTime = section.readFloat('respawnTime')
        self.cooldownTime = section.readFloat('cooldownTime')
        self.unspotDelay = section.readFloat('unspotDelay')
        self.directVisionRadius = section.readFloat('directVisionRadius')
        self.visionMinRadius = section.readFloat('visionMinRadius')
        self.detectFromVehicle = section.readBool('detectFromVehicle')
        self.observationPoints = self._readPointList(*_xml.getSubSectionWithContext(xmlCtx, section, 'observationPoints'))

    @staticmethod
    def _readPointList(xmlCtx, section):
        result = []
        for _, ((_, _), point) in _xml.getItemsWithContext(xmlCtx, section, 'point'):
            result.append(point.asVector3)

        return result


class ReconAbilityEquipment(BaseAbilityEquipment):

    def _readConfig(self, xmlCtx, section):
        super(ReconAbilityEquipment, self)._readConfig(xmlCtx, section)
        self.activatingTime = section.readFloat('activatingTime')
        self.deactivatingTime = section.readFloat('deactivatingTime')


class DistractionAbilityEquipment(BaseAbilityEquipment):

    def _readConfig(self, xmlCtx, section):
        super(DistractionAbilityEquipment, self)._readConfig(xmlCtx, section)
        self.pointRadius = section.readFloat('pointRadius')
        self.detectTime = _xml.readPositiveFloat(xmlCtx, section, 'detectTime', 0.5)
        self.autoDestroyTime = section.readFloat('autoDestroyTime')
        self.changeBrainDelay = section.readFloat('changeBrainDelay')
        self.investigateTime = section.readFloat('investigateTime')
        self.showXrayMarker = section.readBool('showXrayMarker')
        self.detectSequence = section.readString('detectSequence')
