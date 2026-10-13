# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/advanced/data/equipment_alt_key_data.py
import typing
from gui.shared.tooltips.advanced.data.default_alt_key_data import DefaultAltKeyData
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.artefacts import Equipment

class EquipmentAltKeyData(DefaultAltKeyData):
    LEND_LEASE_OIL_EQUIPMENT = 'lendLeaseOil'
    QUALITY_OIL_EQUIPMENT = 'qualityOil'
    ENHANCED_OIL_KEY = 'enhancedOil'
    RATION_KEY = 'ration'

    @classmethod
    def _getDescriptionKey(cls, item, mechanicName):
        if mechanicName in (cls.LEND_LEASE_OIL_EQUIPMENT, cls.QUALITY_OIL_EQUIPMENT):
            return cls.ENHANCED_OIL_KEY
        return cls.RATION_KEY if item.isStimulator else mechanicName

    @staticmethod
    def _getHeader(item, mechanicName):
        return item.shortUserName
