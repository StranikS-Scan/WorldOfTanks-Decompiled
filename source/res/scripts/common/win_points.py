# Embedded file name: scripts/common/win_points.py
import ResMgr
from debug_utils import *
from constants import FLAG_TYPES
_CONFIG_FILE = 'scripts/item_defs/win_points.xml'

class WinPointsTeamSettings:

    def __init__(self, section):
        self.pointsForKill = section['win_points_for_kill'].asInt
        self.pointsForDamage = (section['win_points_for_damage']['damage_to_deal'].asInt, section['win_points_for_damage']['points_to_grant'].asInt)
        self.pointsForFlag = [0] * len(FLAG_TYPES.RANGE)
        for name, subsection in section['win_points_for_flag'].items():
            name = name.upper()
            flagTypeId = getattr(FLAG_TYPES, name, None)
            if flagTypeId is None:
                raise Exception, 'Unknown flag type name (%s)' % (name,)
            self.pointsForFlag[flagTypeId] = subsection.asInt

        self.pointsForOneResource = section['win_points_for_one_resource'].asInt
        return


class WinPointsSoloSettings:

    def __init__(self, section):
        self.pointsForKill = section['win_points_for_kill'].asInt
        self.pointsForDamage = (section['win_points_for_damage']['damage_to_deal'].asInt, section['win_points_for_damage']['points_to_grant'].asInt)
        self.pointsForFlag = [0] * len(FLAG_TYPES.RANGE)
        for name, subsection in section['win_points_for_flag'].items():
            name = name.upper()
            flagTypeId = getattr(FLAG_TYPES, name, None)
            if flagTypeId is None:
                raise Exception, 'Unknown flag type name (%s)' % (name,)
            self.pointsForFlag[flagTypeId] = subsection.asInt

        self.pointsForOneResource = section['win_points_for_one_resource'].asInt
        return


class WinPointsSettings:

    def __init__(self, section):
        self.pointsCAP = section['win_points_cap'].asInt
        self.teamSettings = WinPointsTeamSettings(section['team'])
        self.soloSettings = WinPointsSoloSettings(section['solo'])

    def __getattr__(self, item):
        return lambda isSolo: (getattr(self.soloSettings, item) if isSolo else getattr(self.teamSettings, item))


g_cache = None

def init():
    global g_cache
    g_cache = settings = {}
    section = ResMgr.openSection(_CONFIG_FILE)
    for name, subsection in section.items():
        settings[name] = WinPointsSettings(subsection)
