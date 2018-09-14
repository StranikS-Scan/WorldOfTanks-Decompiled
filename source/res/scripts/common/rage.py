# Embedded file name: scripts/common/rage.py
import ResMgr
from items import vehicles
from debug_utils import *
_CONFIG_FILE = 'scripts/item_defs/rage.xml'

class RageTeamSettings:

    def __init__(self, section):
        self.damageFactor = section['damage_factor'].asFloat
        self.pointsForKill = section['rage_points_for_kill'].asFloat
        self.pointsForFlagPickup = section['rage_points_for_flag_pickup'].asFloat
        self.pointsForFlagCapture = section['rage_points_for_flag_capture'].asFloat
        self.pointsForOneResource = section['rage_points_for_one_resource'].asFloat
        self.deathPenalty = section['death_penalty'].asFloat


class RageSoloSettings:

    def __init__(self, section):
        self.damageFactor = section['damage_factor'].asFloat
        self.pointsForKill = section['rage_points_for_kill'].asFloat
        self.pointsForFlagPickup = section['rage_points_for_flag_pickup'].asFloat
        self.pointsForFlagCapture = section['rage_points_for_flag_capture'].asFloat
        self.pointsForOneResource = section['rage_points_for_one_resource'].asFloat
        self.deathPenalty = section['death_penalty'].asFloat


class RageSettings:

    def __init__(self, section):
        self.pointsLimit = section['rage_points_limit'].asFloat
        self.equipments = {}
        for subsection in section['equipments'].values():
            id = vehicles.g_cache.equipmentIDs()[subsection['name'].asString]
            equipment = vehicles.g_cache.equipments()[id]
            self.equipments[equipment.compactDescr] = subsection['cost_in_rage_points'].asFloat

        self.teamSettings = RageTeamSettings(section['team'])
        self.soloSettings = RageSoloSettings(section['solo'])

    def __getattr__(self, item):
        return lambda isSolo: (getattr(self.soloSettings, item) if isSolo else getattr(self.teamSettings, item))


g_cache = None

def init():
    global g_cache
    section = ResMgr.openSection(_CONFIG_FILE)
    g_cache = RageSettings(section)
