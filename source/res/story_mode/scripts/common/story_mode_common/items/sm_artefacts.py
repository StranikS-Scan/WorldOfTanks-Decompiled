# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/common/story_mode_common/items/sm_artefacts.py
from __future__ import absolute_import
import typing
from items.artefacts import Equipment, AreaOfEffectEquipment, TooltipConfigReader, ArcadeEquipmentConfigReader, AreaMarkerConfigReader
from items.components import component_constants
from items import _xml
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from ResMgr import DataSection
    from Math import Vector3

class SPGZoneEquipment(AreaOfEffectEquipment):
    __slots__ = ('yawHitPrediction', 'hitPredictionDuration')

    def _readConfig(self, xmlCtx, scriptSection):
        super(SPGZoneEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.yawHitPrediction = scriptSection.readInt('yawHitPrediction', 0)
        self.hitPredictionDuration = scriptSection.readFloat('hitPredictionDuration', 0)


class NavmeshSettingsReader(object):
    _SLOTS = ('navmeshGirth', 'navmeshHeightTolerance')

    def initNavmeshConfig(self):
        self.navmeshGirth = component_constants.EMPTY_STRING
        self.navmeshHeightTolerance = component_constants.ZERO_FLOAT

    def readNavmeshConfig(self, xmlCtx, section):
        self.navmeshGirth = section.readString('navmeshGirth')
        if not self.navmeshGirth:
            raise SoftException('[Equipment=<{}>] Param=<navmeshGirth> is required.'.format(self.id))
        self.navmeshHeightTolerance = _xml.readNonNegativeFloat(xmlCtx, section, 'navmeshHeightTolerance', 1.0)


class AOENavmeshEquipment(AreaOfEffectEquipment, NavmeshSettingsReader):
    __slots__ = NavmeshSettingsReader._SLOTS

    def __init__(self):
        super(AOENavmeshEquipment, self).__init__()
        self.initNavmeshConfig()

    def _readConfig(self, xmlCtx, scriptSection):
        super(AOENavmeshEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.readNavmeshConfig(xmlCtx, scriptSection)


class BaseAbilityEquipment(Equipment, TooltipConfigReader, ArcadeEquipmentConfigReader, AreaMarkerConfigReader, NavmeshSettingsReader):
    __slots__ = ('heightAboveBase', 'prepareTime', 'respawnTime', 'cooldownTime', 'unspotDelay', 'directVisionRadius', 'visionMinRadius', 'detectFromVehicle', 'observationPoints') + TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS + AreaMarkerConfigReader._MARKER_SLOTS_ + NavmeshSettingsReader._SLOTS

    def __init__(self):
        super(BaseAbilityEquipment, self).__init__()
        self.initTooltipInformation()
        self.initArcadeInformation()
        self.initMarkerInformation()
        self.initNavmeshConfig()

    def _readConfig(self, xmlCtx, scriptSection):
        super(BaseAbilityEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readArcadeInformation(xmlCtx, scriptSection)
        self.readMarkerConfig(xmlCtx, scriptSection)
        self.readNavmeshConfig(xmlCtx, scriptSection)
        self.prepareTime = scriptSection.readFloat('prepareTime')
        self.respawnTime = scriptSection.readFloat('respawnTime')
        self.cooldownTime = scriptSection.readFloat('cooldownTime')
        self.unspotDelay = scriptSection.readFloat('unspotDelay')
        self.directVisionRadius = scriptSection.readFloat('directVisionRadius')
        self.visionMinRadius = scriptSection.readFloat('visionMinRadius')
        self.detectFromVehicle = scriptSection.readBool('detectFromVehicle')
        self.observationPoints = self._readPointList(*_xml.getSubSectionWithContext(xmlCtx, scriptSection, 'observationPoints'))

    @staticmethod
    def _readPointList(xmlCtx, section):
        result = []
        for _, ((_, _), point) in _xml.getItemsWithContext(xmlCtx, section, 'point'):
            result.append(point.asVector3)

        return result


class ReconAbilityEquipment(BaseAbilityEquipment):

    def _readConfig(self, xmlCtx, scriptSection):
        super(ReconAbilityEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.activatingTime = scriptSection.readFloat('activatingTime')
        self.deactivatingTime = scriptSection.readFloat('deactivatingTime')


class DistractionAbilityEquipment(BaseAbilityEquipment):

    def _readConfig(self, xmlCtx, scriptSection):
        super(DistractionAbilityEquipment, self)._readConfig(xmlCtx, scriptSection)
        self.pointRadius = scriptSection.readFloat('pointRadius')
        self.detectTime = _xml.readPositiveFloat(xmlCtx, scriptSection, 'detectTime', 0.5)
        self.autoDestroyTime = scriptSection.readFloat('autoDestroyTime')
        self.changeBrainDelay = scriptSection.readFloat('changeBrainDelay')
        self.investigateTime = scriptSection.readFloat('investigateTime')
        self.showXrayMarker = scriptSection.readBool('showXrayMarker')
        self.detectSequence = scriptSection.readString('detectSequence')
