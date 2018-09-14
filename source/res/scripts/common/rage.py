# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/rage.py
import ResMgr
from items import vehicles
_CONFIG_FILE = 'scripts/item_defs/rage.xml'

class DamageSettings:

    def __init__(self, section):
        self.damageFactor = section['damageFactor'].asFloat
        self.pointsForKill = section['ragePointsForKill'].asFloat


class RageTeamOrSoloSettings:

    def __init__(self, section):
        self.vehicleDamageSettings = DamageSettings(section['vehicle'])
        self.equipmentDamageSettings = DamageSettings(section['equipment'])
        self.pointsForFlagPickup = section['ragePointsForFlagPickup'].asFloat
        self.pointsForFlagCapture = section['ragePointsForFlagCapture'].asFloat
        self.pointsForOneResource = section['ragePointsForOneResource'].asFloat
        self.deathPenalty = section['deathPenalty'].asFloat


RageTeamSettings = RageTeamOrSoloSettings
RageSoloSettings = RageTeamOrSoloSettings

class RageSettings:

    def __init__(self, section):
        self.pointsLimit = section['ragePointsLimit'].asFloat
        self.equipments = {}
        for subsection in section['equipments'].values():
            id = vehicles.g_cache.equipmentIDs()[subsection['name'].asString]
            equipment = vehicles.g_cache.equipments()[id]
            self.equipments[equipment.compactDescr] = subsection['costInRagePoints'].asFloat

        self.teamSettings = RageTeamSettings(section['team'])
        self.soloSettings = RageSoloSettings(section['solo'])

    def damageFactor(self, isSolo, forVehicle):
        settings = self.soloSettings if isSolo else self.teamSettings
        damageSettings = settings.vehicleDamageSettings if forVehicle else settings.equipmentDamageSettings
        return damageSettings.damageFactor

    def pointsForKill(self, isSolo, forVehicle):
        settings = self.soloSettings if isSolo else self.teamSettings
        damageSettings = settings.vehicleDamageSettings if forVehicle else settings.equipmentDamageSettings
        return damageSettings.pointsForKill

    def __getattr__(self, item):
        if item in ('pointsForFlagPickup', 'pointsForFlagCapture', 'pointsForOneResource', 'deathPenalty'):
            return lambda isSolo: (getattr(self.soloSettings, item) if isSolo else getattr(self.teamSettings, item))
        raise Exception, 'Wrong item to access from RageSettings:%s' % item


g_cache = None

def init():
    global g_cache
    section = ResMgr.openSection(_CONFIG_FILE)
    g_cache = RageSettings(section)
