# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/__init__.py
import imghdr
import itertools
import sys
import inspect
import uuid
import struct
from collections import namedtuple
import BigWorld
import AccountCommands
import Settings
import constants
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_DEBUG, LOG_WARNING
from gui.impl import backport
from gui.impl.gen import R
from helpers import getLanguageCode, i18n
from items import vehicles as vehs_core
from account_helpers import getAccountDatabaseID
from account_helpers.AccountSettings import AccountSettings
from avatar_helpers import getAvatarDatabaseID, getAvatarSessionID
SHELLS_COUNT_PROP_NAME = 'shellsCount'
RELOAD_TIME_SECS_PROP_NAME = 'reloadTimeSecs'
RELOAD_TIME_PROP_NAME = 'reloadTime'
RELOAD_MAGAZINE_TIME_PROP_NAME = 'reloadMagazineTime'
SHELL_RELOADING_TIME_PROP_NAME = 'shellReloadingTime'
DISPERSION_RADIUS_PROP_NAME = 'dispersionRadius'
AIMING_TIME_PROP_NAME = 'aimingTime'
PIERCING_POWER_PROP_NAME = 'piercingPower'
DAMAGE_PROP_NAME = 'damage'
SHELLS_PROP_NAME = 'shells'
STUN_DURATION_PROP_NAME = 'stunDuration'
AUTO_RELOAD_PROP_NAME = 'autoReloadTime'
GUARANTEED_STUN_DURATION_PROP_NAME = 'guaranteedStunDuration'
CLIP_VEHICLES_PROP_NAME = 'clipVehicles'
UNICHARGED_VEHICLES_PROP_NAME = 'uniChargedVehicles'
VEHICLES_PROP_NAME = 'vehicles'
CLIP_VEHICLES_CD_PROP_NAME = 'clipVehiclesCD'
MAX_STEERING_LOCK_ANGLE = 'maxSteeringLockAngle'
WHEELED_SWITCH_ON_TIME = 'wheeledSwitchOnTime'
WHEELED_SWITCH_OFF_TIME = 'wheeledSwitchOffTime'
WHEELED_SWITCH_TIME = 'wheeledSwitchTime'
WHEELED_SPEED_MODE_SPEED = 'wheeledSpeedModeSpeed'
TURBOSHAFT_SWITCH_ON_TIME = 'turboshaftSwitchOnTime'
TURBOSHAFT_SWITCH_OFF_TIME = 'turboshaftSwitchOffTime'
TURBOSHAFT_SWITCH_TIME = 'turboshaftSwitchTime'
TURBOSHAFT_SPEED_MODE_SPEED = 'turboshaftSpeedModeSpeed'
TURBOSHAFT_ENGINE_POWER = 'turboshaftEnginePower'
TURBOSHAFT_INVISIBILITY_STILL_FACTOR = 'turboshaftInvisibilityStillFactor'
TURBOSHAFT_INVISIBILITY_MOVING_FACTOR = 'turboshaftInvisibilityMovingFactor'
DUAL_GUN_CHARGE_TIME = 'chargeTime'
DUAL_GUN_RATE_TIME = 'rateTime'
GUN_RELOADING_TYPE = 'gunReloadingType'
GUN_CAN_BE_CLIP = 1
GUN_CLIP = 2
GUN_NORMAL = 4
GUN_CAN_BE_AUTO_RELOAD = 5
GUN_AUTO_RELOAD = 6
GUN_CAN_BE_DUAL_GUN = 7
GUN_DUAL_GUN = 8
EXTRA_MODULE_INFO = 'extraModuleInfo'
FIELD_SPECIALIZATIONS = 'specs'
FIELD_HIGHLIGHT_TYPE = 'highlightType'
_FLASH_OBJECT_SYS_ATTRS = ('isPrototypeOf', 'propertyIsEnumerable', 'hasOwnProperty')
ValidationResult = namedtuple('ValidationResult', ['isValid', 'reason'])

def flashObject2Dict(obj):
    if hasattr(obj, 'children'):
        filtered = itertools.ifilter(lambda (x, y): x not in _FLASH_OBJECT_SYS_ATTRS, obj.children.iteritems())
        return dict(((k, flashObject2Dict(v)) for k, v in filtered))
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
    return 'Dossiers are unavailable' if code == AccountCommands.RES_CENTER_DISCONNECTED else 'Unknown error code'


def isVehicleObserver(vehTypeCompDescr):
    if vehTypeCompDescr is not None:
        _, nation_id, item_id_within_nation = vehs_core.parseIntCompactDescr(vehTypeCompDescr)
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


def sortByFields(fields, sequence, valueGetter=dict.get):

    def comparator(x, y):
        for field, order in fields:
            fieldValueX = valueGetter(x, field)
            fieldValueY = valueGetter(y, field)
            if fieldValueX != fieldValueY:
                if order:
                    return cmp(fieldValueX, fieldValueY)
                return cmp(fieldValueY, fieldValueX)

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

    except Exception:
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

    def __setattr__(self, name, value):
        if self:
            raise AttributeError("can't set attribute")
        self.__setitem__(name, value)

    def __getattr__(self, item):
        return self.__getitem__(item) if item in self else dict.__getattribute__(self, item)

    def _asdict(self):
        return dict(self)

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, super(SettingRecord, self).__repr__())


class SettingRootRecord(SettingRecord):

    @classmethod
    def load(cls):
        try:
            return cls(**AccountSettings.getSettings(cls._getSettingName()))
        except Exception:
            LOG_ERROR('There is error while unpacking {} settings'.format(cls._getSettingName()), AccountSettings.getSettings(cls._getSettingName()))
            LOG_CURRENT_EXCEPTION()
            return None

        return None

    def save(self):
        return AccountSettings.setSettings(self._getSettingName(), self._asdict())

    @classmethod
    def _getSettingName(cls):
        raise NotImplementedError


def mapTextureToTheMemory(textureData, uniqueID=None, temp=True):
    if textureData and imghdr.what(None, textureData) is not None:
        uniqueID = str(uniqueID or uuid.uuid4())
        if temp:
            BigWorld.wg_addTempScaleformTexture(uniqueID, textureData)
        else:
            BigWorld.wg_addScaleformTexture(uniqueID, textureData)
        return uniqueID
    else:
        LOG_WARNING('There is invalid data for the memory mapping', textureData, uniqueID)
        return


def removeTextureFromMemory(textureID):
    BigWorld.wg_eraseScaleformTexture(textureID)


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
    return float(devidend) / devider if devider > 0 else 0


def weightedAvg(*args):
    values, weights = args
    valSum = 0
    weightSum = 0
    itemsCount = len(values)
    for i in range(itemsCount):
        weight = weights[i]
        valSum += values[i] * weight
        weightSum += weight

    return float(valSum) / weightSum if weightSum != 0 else 0


def makeSearchableString(inputString):
    try:
        return inputString.decode('utf-8').lower()
    except ValueError:
        LOG_ERROR('Given string cannot be decoded from UTF-8', inputString)


def isPopupsWindowsOpenDisabled():
    userPrefs = Settings.g_instance.userPrefs
    ds = userPrefs['development']
    return ds.readBool(Settings.POPUPS_WINDOWS_DISABLED) and constants.IS_DEVELOPMENT if ds is not None else False


_ROMAN_FORBIDDEN_LANGUAGES = {'ko', 'no'}

def isRomanNumberForbidden():
    return bool(_ROMAN_FORBIDDEN_LANGUAGES.intersection((backport.text(R.strings.settings.LANGUAGE_CODE()),)))
