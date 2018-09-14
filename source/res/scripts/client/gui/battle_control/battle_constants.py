# Embedded file name: scripts/client/gui/battle_control/battle_constants.py
from enumerations import Enumeration, AttributeEnumItem

class SHELL_SET_RESULT(object):
    UNDEFINED = 0
    ADDED = 1
    UPDATED = 2
    CURRENT = 4
    CASSETTE_RELOAD = 8


class CANT_SHOOT_ERROR(object):
    UNDEFINED = ''
    WAITING = 'waiting'
    NO_AMMO = 'no_ammo'
    RELOADING = 'gun_reload'


class VEHICLE_VIEW_STATE(object):
    FIRE = 2
    DEVICES = 4
    HEALTH = 8
    DESTROYED = 16
    CREW_DEACTIVATED = 32
    AUTO_ROTATION = 64


VEHICLE_DEVICES = ('engine', 'ammoBay', 'gun', 'turretRotator', 'leftTrack', 'rightTrack', 'surveyingDevice', 'radio', 'fuelTank')
VEHICLE_GUI_ITEMS = ('engine', 'ammoBay', 'gun', 'turretRotator', 'chassis', 'surveyingDevice', 'radio', 'fuelTank')
VEHICLE_DEVICE_IN_COMPLEX_ITEM = {'leftTrack': 'chassis',
 'rightTrack': 'chassis'}
VEHICLE_COMPLEX_ITEMS = {'chassis': ('leftTrack', 'rightTrack')}
DEVICE_STATES_RANGE = ('normal', 'critical', 'destroyed', 'repaired')
DEVICE_STATE_AS_DAMAGE = ('critical', 'destroyed')

class VEHICLE_INDICATOR_TYPE(object):
    DEFAULT = 'Tank'
    SPG = 'SPG'
    AT_SPG = 'AT-SPG'


EXTRA_SUFFIX = 'Health'
EXTRA_PREFIX_LENGTH = len(EXTRA_SUFFIX)

def makeExtraName(entityName):
    return ''.join([entityName, EXTRA_SUFFIX])


PLAYER_ENTITY_NAME = Enumeration("Name of player's entity in the battle", [('ally', {'isFriend': True,
   'base': 'ally'}),
 ('teamKiller', {'isFriend': True,
   'base': 'ally'}),
 ('squadman', {'isFriend': True,
   'base': 'ally'}),
 ('enemy', {'isFriend': False,
   'base': 'enemy'})], instance=AttributeEnumItem)
