# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wotlda/constants.py
import enum

class SupportedWotldaLoadoutType(enum.Enum):
    EASY_TANK_EQUIP = 'easy_tank_equip'
    RANDOM = 'random'
    ONSLAUGHT = 'comp7'
    CREW = 'crew'


class SupportedWTRRange(enum.Enum):
    GOLD = 'gold'
    LEGEND = 'legend'

    @staticmethod
    def allRanges():
        return SupportedWTRRange.__members__.values()


EQUIPMENT_ARCHETYPE_1 = 'equipment_archetype_id_1'
EQUIPMENT_ARCHETYPE_2 = 'equipment_archetype_id_2'
EQUIPMENT_ARCHETYPE_3 = 'equipment_archetype_id_3'
LOADOUT_USAGE_PERCENTAGE = 'usage_percentage'
LAST_UPDATE_TIMESTAMP = 'updated_at'
ExpectedArchetypes = {'improvedConfiguration',
 'improvedVentilation',
 'tankRammer',
 'coatedOptics',
 'aimingStabilizer',
 'enhancedAimDrives',
 'antifragmentationLining',
 'stereoscope',
 'camouflageNet',
 'grousers',
 'additionalInvisibilityDevice',
 'extraHealthReserve',
 'improvedRadioCommunication',
 'improvedRotationMechanism',
 'turbocharger',
 'commandersView',
 'improvedSights',
 'modernizedAimDrivesAimingStabilizer',
 'modernizedTurbochargerRotationMechanism',
 'modernizedExtraHealthReserveAntifragmentationLining',
 'modernizedImprovedSightsEnhancedAimDrives'}

class OptDeviceAssistType(enum.Enum):
    NODATA = 0
    NORMAL = 1
    LINKED = 2
    COMBINED = 3
