# Embedded file name: scripts/client/gui/shared/utils/__init__.py
import imghdr
import itertools
import sys
import inspect
import uuid
import struct
import BigWorld
import AccountCommands
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_DEBUG, LOG_WARNING
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from helpers import getLanguageCode, i18n
from items import vehicles as vehs_core
from account_helpers import getAccountDatabaseID
from account_helpers.AccountSettings import AccountSettings
from avatar_helpers import getAvatarDatabaseID
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
CLIP_ICON_PATH = RES_ICONS.MAPS_ICONS_MODULES_MAGAZINEGUNICON
EXTRA_MODULE_INFO = 'extraModuleInfo'
_FLASH_OBJECT_SYS_ATTRS = ('isPrototypeOf', 'propertyIsEnumerable', 'hasOwnProperty')

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
    if vehTypeCompDescr is not None:
        item_type_id, nation_id, item_id_within_nation = vehs_core.parseIntCompactDescr(vehTypeCompDescr)
        return 'observer' in vehs_core.g_cache.vehicle(nation_id, item_id_within_nation).tags
    else:
        return False


def class_for_name(module_name, class_name):
    __import__(module_name)
    m = sys.modules[module_name]
    c = getattr(m, class_name)
    if not inspect.isclass(c):
        LOG_ERROR('%s - is not a class, check module path or className' % class_name)
        return None
    else:
        return c


def sortByFields(fields, sequence, valueGetter = dict.get):

    def comparator(x, y):
        for field, order in fields:
            fieldValueX = valueGetter(x, field)
            fieldValueY = valueGetter(y, field)
            if fieldValueX != fieldValueY:
                if order:
                    return cmp(fieldValueX, fieldValueY)
                return cmp(fieldValueY, fieldValueX)

        return 0

    return sorted(sequence, cmp=comparator)


def roundByModulo(value, rate):
    left = value % rate
    if left > 0:
        value += rate - left
    return value


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


def copyToClipboard(text):
    BigWorld.wg_copyToClipboard(unicode(text, 'utf-8', errors='ignore'))
    LOG_DEBUG('Text has been copied to the clipboard', text)


class SettingRecord(dict):

    def __init__(self, *args, **kwargs):
        super(SettingRecord, self).__init__(*args, **kwargs)

    def __setattr__(self, name, value):
        if len(self):
            raise AttributeError("can't set attribute")
        self.__setitem__(name, value)

    def __getattr__(self, item):
        if item in self:
            return self.__getitem__(item)
        return dict.__getattribute__(self, item)

    def _asdict(self):
        return dict(self)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, super(SettingRecord, self).__repr__())


class SettingRootRecord(SettingRecord):

    @classmethod
    def load(cls):
        try:
            return cls(**AccountSettings.getSettings(cls._getSettingName()))
        except:
            LOG_ERROR('There is error while unpacking quests settings', AccountSettings.getSettings('quests'))
            LOG_CURRENT_EXCEPTION()
            return None

        return None

    def save(self):
        return AccountSettings.setSettings(self._getSettingName(), self._asdict())

    @classmethod
    def _getSettingName(cls):
        raise NotImplemented


def mapTextureToTheMemory(textureData, uniqueID = None):
    if textureData and imghdr.what(None, textureData) is not None:
        uniqueID = str(uniqueID or uuid.uuid4())
        BigWorld.wg_addTempScaleformTexture(uniqueID, textureData)
        return uniqueID
    else:
        LOG_WARNING('There is invalid data for the memory mapping', textureData, uniqueID)
        return


def getImageSize(imageData):
    width, height = (None, None)
    if imageData:
        imgType = imghdr.what(None, imageData)
        if imgType == 'png':
            check = struct.unpack('>i', imageData[4:8])[0]
            if check != 218765834:
                return
            width, height = struct.unpack('>ii', imageData[16:24])
        elif imgType == 'gif':
            width, height = struct.unpack('<HH', imageData[6:10])
        elif imgType == 'jpeg':
            LOG_WARNING('JPEG image type is not supported')
            width, height = (None, None)
    return (width, height)


def showInvitationInWindowsBar():
    try:
        BigWorld.WGWindowsNotifier.onInvitation()
    except AttributeError:
        LOG_CURRENT_EXCEPTION()


def getPlayerDatabaseID():
    return getAccountDatabaseID() or getAvatarDatabaseID()


def getPlayerName():
    return getattr(BigWorld.player(), 'name', '')


def avg(devidend, devider):
    if devider > 0:
        return devidend / devider
    return 0


def weightedAvg(*args):
    values, weights = args
    valSum = 0
    weightSum = 0
    itemsCount = len(values)
    for i in range(itemsCount):
        weight = weights[i]
        valSum += values[i] * weight
        weightSum += weight

    if weightSum != 0:
        return float(valSum) / weightSum
    else:
        return 0
