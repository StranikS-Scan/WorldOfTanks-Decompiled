# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/win_points.py
import ResMgr
from constants import FLAG_TYPES_INDICES
_CONFIG_FILE = 'scripts/item_defs/win_points.xml'

class DamageSettingsEmpty(object):

    def __init__(self):
        self.pointsForKill = 0
        self.pointsForDamage = (0, 0)


class DamageSettings(DamageSettingsEmpty):

    def __init__(self, section):
        super(DamageSettings, self).__init__()
        self.pointsForKill = section['winPointsForKill'].asInt
        self.pointsForDamage = (section['winPointsForDamage']['damageToDeal'].asInt, section['winPointsForDamage']['pointsToGrant'].asInt)


class WinPointsGroupSettingsEmpty(object):

    def __init__(self):
        self.damageSettingsForVehicle = DamageSettingsEmpty()
        self.damageSettingsForEquipment = DamageSettingsEmpty()


class WinPointsGroupSettings(WinPointsGroupSettingsEmpty):

    def __init__(self, section):
        super(WinPointsGroupSettings, self).__init__()
        self.damageSettingsForVehicle = self.__getDamageSettingsFor(section['vehicle'])
        self.damageSettingsForEquipment = self.__getDamageSettingsFor(section['equipment'])

    def __getDamageSettingsFor(self, section):
        return DamageSettings(section) if section else DamageSettingsEmpty()


class WinPointsSettings(object):

    def __init__(self, section):
        self.pointsCAP = section.readInt('winPointsCAP', 0)
        self.pointsForBaseCaptured = section.readInt('pointsForBaseCaptured', 0)
        self.team = self.__getSettingsFor(section['team'])
        self.avatar = self.__getSettingsFor(section['avatar'])

    def __getSettingsFor(self, section):
        return WinPointsGroupSettings(section) if section else WinPointsGroupSettingsEmpty()


g_cache = None

def init():
    global g_cache
    g_cache = settings = {}
    section = ResMgr.openSection(_CONFIG_FILE)
    for name, subsection in section.items():
        settings[name] = WinPointsSettings(subsection)
