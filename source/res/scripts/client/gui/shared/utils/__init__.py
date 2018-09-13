# Embedded file name: scripts/client/gui/shared/utils/__init__.py
import weakref
import types
import itertools
import BigWorld
import AccountCommands
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG
from helpers import getLanguageCode, i18n
from items import vehicles as vehs_core
ScalarTypes = (types.IntType,
 types.LongType,
 types.FloatType,
 types.BooleanType) + types.StringTypes
SHELLS_COUNT_PROP_NAME = 'shellsCount'
RELOAD_TIME_PROP_NAME = 'reloadTime'
RELOAD_MAGAZINE_TIME_PROP_NAME = 'reloadMagazineTime'
SHELL_RELOADING_TIME_PROP_NAME = 'shellReloadingTime'
DISPERSION_RADIUS_PROP_NAME = 'dispersionRadius'
AIMING_TIME_PROP_NAME = 'aimingTime'
PIERCING_POWER_PROP_NAME = 'piercingPower'
DAMAGE_PROP_NAME = 'damage'
SHELLS_PROP_NAME = 'shells'
CLIP_VEHICLES_PROP_NAME = 'clipVehicles'
UNICHARGED_VEHICLES_PROP_NAME = 'uniChargedVehicles'
VEHICLES_PROP_NAME = 'vehicles'
CLIP_VEHICLES_CD_PROP_NAME = 'clipVehiclesCD'
GUN_RELOADING_TYPE = 'gunReloadingType'
GUN_CAN_BE_CLIP = 1
GUN_CLIP = 2
GUN_NORMAL = 4
CLIP_ICON_PATH = '../maps/icons/modules/magazineGunIcon.png'
EXTRA_MODULE_INFO = 'extraModuleInfo'
_FLASH_OBJECT_SYS_ATTRS = ('isPrototypeOf', 'propertyIsEnumerable', 'hasOwnProperty')

class CONST_CONTAINER:
    __keyByValue = None

    @classmethod
    def getIterator(cls):
        for k, v in cls.__dict__.iteritems():
            if not k.startswith('_') and type(v) in ScalarTypes:
                yield (k, v)

    @classmethod
    def getKeyByValue(cls, value):
        if cls.__keyByValue is None:
            cls.__keyByValue = dict(((v, k) for k, v in cls.getIterator()))
        return cls.__keyByValue.get(value)

    @classmethod
    def ALL(cls):
        return tuple([ v for k, v in cls.getIterator() ])


class BitmaskHelper(object):

    @classmethod
    def add(cls, mask, flag):
        if not mask & flag:
            mask |= flag
            return mask
        return -1

    @classmethod
    def addIfNot(cls, mask, flag):
        if not mask & flag:
            mask |= flag
        return mask

    @classmethod
    def remove(cls, mask, flag):
        if mask & flag > 0:
            mask ^= flag
            return mask
        return -1

    @classmethod
    def removeIfHas(cls, mask, flag):
        if mask & flag > 0:
            mask ^= flag
        return mask


def flashObject2Dict(obj):
    if hasattr(obj, 'children'):
        return dict(map(lambda (k, v): (k, flashObject2Dict(v)), itertools.ifilter(lambda (x, y): x not in _FLASH_OBJECT_SYS_ATTRS, obj.children.iteritems())))
    return obj


def code2str(code):
    if code == AccountCommands.RES_SUCCESS:
        return 'Request succedded'
    if code == AccountCommands.RES_STREAM:
        return 'Stream is sent to the client'
    if code == AccountCommands.RES_CACHE:
        return 'Data is taken from cache'
    if code == AccountCommands.RES_FAILURE:
        return 'Unknown reason'
    if code == AccountCommands.RES_WRONG_ARGS:
        return 'Wrong arguments'
    if code == AccountCommands.RES_NON_PLAYER:
        return 'Account become non player'
    if code == AccountCommands.RES_SHOP_DESYNC:
        return 'Shop cache is desynchronized'
    if code == AccountCommands.RES_COOLDOWN:
        return 'Identical requests cooldown'
    if code == AccountCommands.RES_HIDDEN_DOSSIER:
        return 'Player dossier is hidden'
    if code == AccountCommands.RES_CENTER_DISCONNECTED:
        return 'Dossiers are unavailable'
    return 'Unknown error code'


def isVehicleObserver(vehTypeCompDescr):
    item_type_id, nation_id, item_id_within_nation = vehs_core.parseIntCompactDescr(vehTypeCompDescr)
    return 'observer' in vehs_core.g_cache.vehicle(nation_id, item_id_within_nation).tags


class BoundMethodWeakref(object):

    def __init__(self, func):
        self.methodName = func.__name__
        self.wrefCls = weakref.ref(func.__self__)

    def __call__(self, *args, **kwargs):
        return getattr(self.wrefCls(), self.methodName)(*args, **kwargs)


def findFirst(function_or_None, sequence, default = None):
    try:
        return next(itertools.ifilter(function_or_None, sequence))
    except StopIteration:
        return default


def prettyPrint(dict, sort_keys = True, indent = 4):
    import json
    return json.dumps(dict, sort_keys=sort_keys, indent=indent)


_STR_CASING_OPTIONS = {'el': (8, 1, 0),
 'ro': (24, 1, 0),
 'tr': (31, 1, 0)}
_REPLACEMENTS = {'el': (u'\u0386\u0388\u038a\u0389\u038e\u038c\u038f', u'\u0391\u0395\u0399\u0397\u03a5\u039f\u03a9')}

def changeStringCasing(string, isUpper):
    langID = getLanguageCode()
    try:
        string = string.decode('utf-8')
        if langID is not None:
            langID = str(langID).lower()
            if langID in _STR_CASING_OPTIONS:
                plID, slID, sortOrder = _STR_CASING_OPTIONS[langID]
                string = BigWorld.wg_changeStringCasing(string, plID, slID, sortOrder, isUpper)
            else:
                string = string.upper() if isUpper else string.lower()
            if langID in _REPLACEMENTS:
                for wrong, right in zip(*_REPLACEMENTS[langID]):
                    string = string.replace(wrong, right)

    except:
        LOG_CURRENT_EXCEPTION()

    return i18n.encodeUtf8(string)


def toLower(string):
    return changeStringCasing(string, False)


def toUpper(string):
    return changeStringCasing(string, True)


class AlwaysValidObject(object):

    def __init__(self, name = ''):
        self.__name = name

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        return AlwaysValidObject(self._makeName(self.__name, item))

    def __call__(self, *args, **kwargs):
        return AlwaysValidObject()

    def getName(self):
        return self.__name

    @classmethod
    def _makeName(cls, parentName, nodeName):
        return '%s/%s' % (parentName, nodeName)
