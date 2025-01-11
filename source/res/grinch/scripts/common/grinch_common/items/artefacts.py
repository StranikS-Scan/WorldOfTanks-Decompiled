# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/common/grinch_common/items/artefacts.py
import items.artefacts as artefacts

class GrinchVisualScriptEquipment(artefacts.VisualScriptEquipment, artefacts.AbilityTooltipConfigReader):
    __slots__ = ('radius', 'duration', 'debuffDuration')

    def __init__(self):
        super(GrinchVisualScriptEquipment, self).__init__()
        self.initTooltipsInformation()

    def _readConfig(self, xmlCtx, section):
        super(GrinchVisualScriptEquipment, self)._readConfig(xmlCtx, section)
        self.readTooltipsConfig(xmlCtx, section)


class GrinchAimingVisualScriptEquipment(artefacts.VisualScriptEquipment, artefacts.AreaMarkerConfigReader, artefacts.ArcadeEquipmentConfigReader, artefacts.AbilityTooltipConfigReader):
    __slots__ = ()

    def __init__(self):
        super(GrinchAimingVisualScriptEquipment, self).__init__()
        self.initMarkerInformation()
        self.initArcadeInformation()
        self.initTooltipsInformation()

    def _readConfig(self, xmlCtx, section):
        super(GrinchAimingVisualScriptEquipment, self)._readConfig(xmlCtx, section)
        self.readMarkerConfig(xmlCtx, section)
        self.readArcadeInformation(xmlCtx, section)
        self.readTooltipsConfig(xmlCtx, section)
