# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/bonus_readers.py
import time
from typing import Union, TYPE_CHECKING
import dossiers2
from dynamic_currencies import g_dynamicCurrenciesData
import items
import calendar
from account_shared import validateCustomizationItem
from battle_pass_common import NON_VEH_CD
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentTypes import isUniversalFragment
from dossiers2.custom.account_layout import ACCOUNT_DOSSIER_DICT_BLOCKS
from dossiers2.custom.cache import getCache
from invoices_helpers import checkAccountDossierOperation
from items import vehicles, tankmen, utils
from items.components.c11n_constants import SeasonType
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from constants import DOSSIER_TYPE, IS_DEVELOPMENT, SEASON_TYPE_BY_NAME, EVENT_TYPE, INVOICE_LIMITS, ENTITLEMENT_OPS, DailyQuestsLevels, MAX_LOG_EXT_INFO_LEN
from soft_exception import SoftException
from customization_quests_common import validateCustomizationQuestToken
if TYPE_CHECKING:
    from ResMgr import DataSection
__all__ = ['readBonusSection', 'readUTC', 'SUPPORTED_BONUSES']

def bonusReaderLimitDecorator(invoiceLimit, readFunction):

    def wrapper(bonus, name, section, eventType, checkLimit):
        readFunction(bonus, name, section, eventType, checkLimit)
        if checkLimit and bonus[name] > invoiceLimit:
            raise SoftException('Invalid count of %s with amount %d when limit is %d. ' % (name, bonus[name], invoiceLimit))

    return wrapper


def getBonusReaders(bonusTypes):
    return dict(((k, __BONUS_READERS[k]) for k in bonusTypes))


def timeDataToUTC(timeData, default=None):
    try:
        if timeData is None:
            raise SoftException('Wrong timeData')
        if timeData != '':
            timeData = int(calendar.timegm(time.strptime(timeData, '%d.%m.%Y %H:%M')))
        else:
            return default
    except:
        raise SoftException('Invalid format (%s). Format must be like %s, for example 23.01.2011 00:00.' % (timeData, "'%d.%m.%Y %H:%M'"))

    return timeData


def readUTC(section, field, default=None):
    timeData = section.readString(field, '')
    try:
        return timeDataToUTC(timeData, default)
    except Exception as e:
        raise SoftException('Invalid field %s: %s' % (field, e))


def __readBonus_bool(bonus, name, section, eventType, checkLimit):
    bonus[name] = section.asBool


def __readBonus_string_set(bonus, name, section, eventType, checkLimit):
    data = section.asString
    bonus[name] = data.strip().split()


def checkLogExtInfoLen(info, infoName):
    if len(info) > MAX_LOG_EXT_INFO_LEN:
        raise SoftException('Length of %s id "%s" is %d more than max length %d' % (infoName,
         id,
         len(info),
         MAX_LOG_EXT_INFO_LEN))


class IntHolder(int):
    newval = 0
    rate = 1

    def __new__(cls, value, **kwargs):
        return super(IntHolder, cls).__new__(cls, value, **{k:v for k, v in kwargs.iteritems() if k in ('base',)})

    def __init__(self, value, **kwargs):
        super(IntHolder, self).__init__()
        self.ukey = kwargs.get('ukey')
        self.rate = int(kwargs.get('rate', self.rate))
        self._materialized = False

    def materialize(self, substitutions):
        if self.ukey is not None and substitutions and not self.isMaterialized():
            self.newval = substitutions.get(self.ukey, 0)
            self.newval = int(max(0, self.newval * self.rate))
            self._materialized = True
        return int(self)

    def isMaterialized(self):
        return self._materialized

    def __int__(self):
        return self.newval if self.isMaterialized() else super(IntHolder, self).__int__()

    def __repr__(self):
        return int(self).__repr__()

    def bit_length(self):
        return int(self).bit_length()

    def __add__(self, x):
        return int(self).__add__(x)

    def __sub__(self, x):
        return int(self).__sub__(x)

    def __mul__(self, x):
        return int(self).__mul__(x)

    def __floordiv__(self, x):
        return int(self).__floordiv__(x)

    def __div__(self, x):
        return int(self).__div__(x)

    def __truediv__(self, x):
        return int(self).__truediv__(x)

    def __mod__(self, x):
        return int(self).__mod__(x)

    def __divmod__(self, x):
        return int(self).__divmod__(x)

    def __radd__(self, x):
        return int(self).__radd__(x)

    def __rsub__(self, x):
        return int(self).__rsub__(x)

    def __rmul__(self, x):
        return int(self).__rmul__(x)

    def __rfloordiv__(self, x):
        return int(self).__rfloordiv__(x)

    def __rdiv__(self, x):
        return int(self).__rdiv__(x)

    def __rtruediv__(self, x):
        return int(self).__rtruediv__(x)

    def __rmod__(self, x):
        return int(self).__rmod__(x)

    def __rdivmod__(self, x):
        return int(self).__rdivmod__(x)

    def __pow__(self, x):
        return int(self).__pow__(x)

    def __rpow__(self, x):
        return int(self).__rpow__(x)

    def __and__(self, n):
        return int(self).__and__(n)

    def __or__(self, n):
        return int(self).__or__(n)

    def __xor__(self, n):
        return int(self).__xor__(n)

    def __lshift__(self, n):
        return int(self).__lshift__(n)

    def __rshift__(self, n):
        return int(self).__rshift__(n)

    def __rand__(self, n):
        return int(self).__rand__(n)

    def __ror__(self, n):
        return int(self).__ror__(n)

    def __rxor__(self, n):
        return int(self).__rxor__(n)

    def __rlshift__(self, n):
        return int(self).__rlshift__(n)

    def __rrshift__(self, n):
        return int(self).__rrshift__(n)

    def __neg__(self):
        return int(self).__neg__()

    def __pos__(self):
        return int(self).__pos__()

    def __invert__(self):
        return int(self).__invert__()

    def __eq__(self, x):
        return int(self) == x

    def __ne__(self, x):
        return int(self) != x

    def __lt__(self, x):
        return int(self) < x

    def __le__(self, x):
        return int(self) <= x

    def __gt__(self, x):
        return int(self) > x

    def __ge__(self, x):
        return int(self) >= x

    def __str__(self):
        return '{}: [val = {}, ukey = {}, rate = {}, isMaterialized = {}]'.format(self.__class__.__name__, int(self), self.ukey, self.rate, self.isMaterialized())

    def __float__(self):
        return int(self).__float__()

    def __abs__(self):
        return int(self).__abs__()

    def __hash__(self):
        return object.__hash__(self)

    def __nonzero__(self):
        return int(self).__nonzero__()


class FloatHolder(float):
    newval = 0.0
    rate = 1.0

    def __new__(cls, value, **kwargs):
        return super(FloatHolder, cls).__new__(cls, value)

    def __init__(self, value, **kwargs):
        super(FloatHolder, self).__init__()
        self.ukey = kwargs.get('ukey')
        self.rate = float(kwargs.get('rate', self.rate))
        self._materialized = False

    def materialize(self, substitutions):
        if self.ukey is not None and substitutions and not self.isMaterialized():
            self.newval = substitutions.get(self.ukey, 0.0)
            self.newval = float(max(0.0, self.newval * self.rate))
            self._materialized = True
        return float(self)

    def isMaterialized(self):
        return self._materialized

    def __float__(self):
        return self.newval if self.isMaterialized() else super(FloatHolder, self).__float__()

    def __repr__(self):
        return float(self).__repr__()

    def as_integer_ratio(self):
        return float(self).as_integer_ratio()

    def hex(self):
        return float(self).hex()

    def is_integer(self):
        return float(self).is_integer()

    @classmethod
    def fromhex(cls, s):
        return super(FloatHolder, cls).fromhex(s)

    def __add__(self, x):
        return float(self).__add__(x)

    def __sub__(self, x):
        return float(self).__sub__(x)

    def __mul__(self, x):
        return float(self).__mul__(x)

    def __floordiv__(self, x):
        return float(self).__floordiv__(x)

    def __div__(self, x):
        return float(self).__div__(x)

    def __truediv__(self, x):
        return float(self).__truediv__(x)

    def __mod__(self, x):
        return float(self).__mod__(x)

    def __divmod__(self, x):
        return float(self).__divmod__(x)

    def __pow__(self, x):
        return float(self).__pow__(x)

    def __radd__(self, x):
        return float(self).__radd__(x)

    def __rsub__(self, x):
        return float(self).__rsub__(x)

    def __rmul__(self, x):
        return float(self).__rmul__(x)

    def __rfloordiv__(self, x):
        return float(self).__rfloordiv__(x)

    def __rdiv__(self, x):
        return float(self).__rdiv__(x)

    def __rtruediv__(self, x):
        return float(self).__rtruediv__(x)

    def __rmod__(self, x):
        return float(self).__rmod__(x)

    def __rdivmod__(self, x):
        return float(self).__rdivmod__(x)

    def __rpow__(self, x):
        return float(self).__rpow__(x)

    def __eq__(self, x):
        return float(self).__eq__(x)

    def __ne__(self, x):
        return float(self).__ne__(x)

    def __lt__(self, x):
        return float(self).__lt__(x)

    def __le__(self, x):
        return float(self).__le__(x)

    def __gt__(self, x):
        return float(self).__gt__(x)

    def __ge__(self, x):
        return float(self).__ge__(x)

    def __neg__(self):
        return float(self).__neg__()

    def __pos__(self):
        return float(self).__pos__()

    def __str__(self):
        return float(self).__str__()

    def __int__(self):
        return float(self).__int__()

    def __abs__(self):
        return float(self).__abs__()

    def __hash__(self):
        return object.__hash__(self)

    def __nonzero__(self):
        return float(self).__nonzero__()


def __readIntWithTokenExpansion(section):
    bindingToken = section.readString('token2int', '')
    rate = section.readInt('rate', 1)
    value = section.asInt
    if value < 0:
        raise SoftException('Negative value (%s)' % section.name)
    return IntHolder(value, ukey=bindingToken, rate=rate) if bindingToken else value


def __readBonus_int(bonus, name, section, eventType, checkLimit):
    bonus[name] = __readIntWithTokenExpansion(section)


def __readBonus_factor(bonus, name, section, eventType, checkLimit):
    bindingToken = section.readString('token2float', '')
    rate = section.readFloat('rate', 1.0)
    value = section.asFloat
    if value < 0:
        raise SoftException('Negative value (%s)' % name)
    bonus[name] = FloatHolder(value, ukey=bindingToken, rate=rate) if bindingToken else value


def __readBonus_equipment(bonus, _name, section, eventType, checkLimit):
    eqName = section.asString
    cache = vehicles.g_cache
    eqID = cache.equipmentIDs().get(eqName)
    if eqID is None:
        raise SoftException("Unknown equipment '%s'" % eqName)
    eqCompDescr = cache.equipments()[eqID].compactDescr
    count = 1
    if section.has_key('count'):
        count = section['count'].asInt
    bonus.setdefault('items', {})[eqCompDescr] = count
    return


def __readBonus_optionalDevice(bonus, _name, section, eventType, checkLimit):
    name = section.asString
    cache = vehicles.g_cache
    odID = cache.optionalDeviceIDs().get(name)
    if odID is None:
        raise SoftException("Unknown optional device '%s'" % name)
    odCompDescr = cache.optionalDevices()[odID].compactDescr
    count = 1
    if section.has_key('count'):
        count = section['count'].asInt
    bonus.setdefault('items', {})[odCompDescr] = count
    return


def __readBonus_item(bonus, _name, section, eventType, checkLimit):
    compDescr = section.asInt
    try:
        descr = utils.getItemDescrByCompactDescr(compDescr)
        if descr.itemTypeName not in items.SIMPLE_ITEM_TYPE_NAMES:
            raise SoftException('Wrong compact descriptor (%d). Not simple item.' % compDescr)
    except:
        raise SoftException('Wrong compact descriptor (%d)' % compDescr)

    count = 1
    if section.has_key('count'):
        count = section['count'].asInt
    bonus.setdefault('items', {})[compDescr] = count


def __readBonus_vehicle(bonus, _name, section, eventType, checkLimit):
    vehCompDescr = None
    if section.has_key('vehCompDescr'):
        vehCompDescr = section['vehCompDescr'].asString.decode('base64')
        vehTypeCompDescr = vehicles.VehicleDescr(vehCompDescr).type.compactDescr
    elif section.has_key('vehTypeCompDescr'):
        vehTypeCompDescr = section['vehTypeCompDescr'].asInt
    else:
        nationID, innationID = vehicles.g_list.getIDsByName(section.asString)
        vehTypeCompDescr = vehicles.makeIntCompactDescrByID('vehicle', nationID, innationID)
    extra = {}
    if section.has_key('tankmen'):
        __readBonus_tankmen(extra, vehTypeCompDescr, section['tankmen'], eventType, checkLimit)
    else:
        if section.has_key('noCrew'):
            extra['noCrew'] = True
        if section.has_key('crewLvl'):
            extra['crewLvl'] = section['crewLvl'].asInt
        if section.has_key('crewFreeXP'):
            extra['crewFreeXP'] = section['crewFreeXP'].asInt
    if section.has_key('rent'):
        __readBonus_rent(extra, None, section['rent'])
    if section.has_key('customization'):
        __readBonus_vehicleCustomizations(extra, None, section['customization'])
    if section.has_key('customCompensation'):
        __readBonus_customCompensation(extra, None, section['customCompensation'])
    if section.has_key('customCompensationDetails'):
        __readBonus_customCompensationDetails(extra, None, section['customCompensationDetails'])
    if section.has_key('outfits'):
        __readBonus_outfits(extra, None, section['outfits'])
    if section.has_key('ammo'):
        ammo = section['ammo'].asString
        extra['ammo'] = [ int(item) for item in ammo.split(' ') ]
    if section.has_key('unlock'):
        extra['unlock'] = True
    if section.has_key('unlockModules'):
        extra['unlockModules'] = True
    if section.has_key('bonusOrder'):
        extra['bonusOrder'] = section['bonusOrder'].asInt
    vehicleBonuses = bonus.setdefault('vehicles', {})
    vehKey = vehCompDescr if vehCompDescr else vehTypeCompDescr
    if vehKey in vehicleBonuses:
        raise SoftException('Duplicate vehicle', vehKey)
    vehicleBonuses[vehKey] = extra
    return


def __readBonus_customCompensation(bonus, _name, section):
    credits = section.readInt('credits', 0)
    gold = section.readInt('gold', 0)
    bonus['customCompensation'] = (credits, gold)


def __readBonus_customCompensationDetails(bonus, _name, section):
    bonus['customCompensationDetails'] = {}
    if section.has_key('noCrew'):
        bonus['customCompensationDetails']['noCrew'] = True


def __readBonus_vehicleCustomizations(bonus, _name, section):
    custData = {'value': 1,
     'custType': 'style',
     'id': section.readInt('styleId', -1)}
    if section.has_key('customCompensation'):
        __readBonus_customCompensation(custData, None, section['customCompensation'])
    if section.has_key('serialNumberSequence'):
        custData['serialNumberSequence'] = section.readString('serialNumberSequence')
    isValid, item = validateCustomizationItem(custData)
    if not isValid:
        raise SoftException(item)
    bonus['customization'] = {'styleId': custData['id'],
     'customCompensation': custData['customCompensation']}
    if 'serialNumberSequence' in custData:
        bonus['customization']['serialNumberSequence'] = custData['serialNumberSequence']
    return


def __readBonus_tankmen(bonus, vehTypeCompDescr, section, eventType, checkLimit):
    lst = []
    for subsection in section.values():
        tmanDescr = subsection.asString
        if tmanDescr:
            try:
                tman = tankmen.TankmanDescr(tmanDescr)
                if type(vehTypeCompDescr) == int:
                    _, vehNationID, vehicleTypeID = vehicles.parseIntCompactDescr(vehTypeCompDescr)
                    if vehNationID != tman.nationID or vehicleTypeID != tman.vehicleTypeID:
                        raise SoftException('Vehicle and tankman mismatch.')
            except Exception as e:
                raise SoftException('Invalid tankmen compact descr. Error: %s' % (e,))

            lst.append(tmanDescr)
            continue
        tmanData = {'isFemale': subsection.readBool('isFemale', False),
         'firstNameID': subsection.readInt('firstNameID', -1),
         'lastNameID': subsection.readInt('lastNameID', -1),
         'role': subsection.readString('role', ''),
         'iconID': subsection.readInt('iconID', -1),
         'freeXP': subsection.readInt('freeXP', 0),
         'fnGroupID': subsection.readInt('fnGroupID', 0),
         'lnGroupID': subsection.readInt('lnGroupID', 0),
         'iGroupID': subsection.readInt('iGroupID', 0),
         'isPremium': subsection.readBool('isPremium', False),
         'nationID': subsection.readInt('nationID', -1),
         'vehicleTypeID': subsection.readInt('vehicleTypeID', -1),
         'skills': subsection.readString('skills', '').split(),
         'freeSkills': subsection.readString('freeSkills', '').split()}
        if checkLimit and tmanData['freeXP'] > INVOICE_LIMITS.TMAN_FREEXP_MAX:
            raise SoftException('Invalid count of tankman free xp with amount %d when limit is %d.' % (tmanData['freeXP'], INVOICE_LIMITS.TMAN_FREEXP_MAX))
        if checkLimit and len(tmanData['skills']) > INVOICE_LIMITS.TMAN_SKILLS_MAX:
            raise SoftException('Invalid count of tankman skills with amount %d when limit is %d.' % (len(tmanData['skills']), INVOICE_LIMITS.TMAN_SKILLS_MAX))
        for record in ('firstNameID', 'lastNameID', 'iconID'):
            if tmanData[record] == -1:
                tmanData[record] = None

        try:
            if type(vehTypeCompDescr) == int:
                _, vehNationID, vehicleTypeID = vehicles.parseIntCompactDescr(vehTypeCompDescr)
                if vehNationID != tmanData['nationID'] or vehicleTypeID != tmanData['vehicleTypeID']:
                    raise SoftException('Vehicle and tankman mismatch.')
            if eventType != EVENT_TYPE.PERSONAL_MISSION:
                tmanData = tankmen.makeTmanDescrByTmanData(tmanData)
            lst.append(tmanData)
        except Exception as e:
            raise SoftException('%s: %s' % (e, tmanData))

    bonus['tankmen'] = lst
    return


def __readBonus_seasonRent(outRent, section):
    if section.has_key('season'):
        try:
            seasonData = section['season'].asString.split(':', 1)
            seasonType = SEASON_TYPE_BY_NAME[seasonData[0].strip()]
            strID = seasonData[1]
            if strID.startswith('season_'):
                rentType = 'season'
            elif strID.startswith('cycle_'):
                rentType = 'cycle'
            else:
                raise SoftException('Invalid season / cycle ID in rent bonus <rent><season>. Expected format: GameSeasonType:season_YYYYMM or                 GameSeasonType:cycle_YYYYMMDD')
            ID = int(strID.split('_', 1)[1].strip())
            outRent[rentType] = [(seasonType, ID)]
        except (KeyError, ValueError):
            raise SoftException('Failed to parse season rent bonus for <rent><{type}>. Expected format: GameSeasonType:season_YYYYMM or                 GameSeasonType:cycle_YYYYMMDD')


def __readBonus_rent(bonus, _name, section):
    rent = {}
    anySectionExist = False
    if section.has_key('anyExpires'):
        rent['anyExpires'] = anySectionExist = True
    if section.has_key('time'):
        rent['time'] = section['time'].asFloat
    if section.has_key('battles'):
        rent['battles'] = section['battles'].asInt
    if section.has_key('wins'):
        rent['wins'] = section['wins'].asInt
    if anySectionExist:
        for key in ('time', 'battles', 'wins'):
            rent[key] = rent[key] if key in rent and rent[key] > 0 else float('inf')

    if section.has_key('compensation'):
        credits = section['compensation'].readInt('credits', 0)
        gold = section['compensation'].readInt('gold', 0)
        rent['compensation'] = (credits, gold)
    __readBonus_seasonRent(rent, section)
    bonus['rent'] = rent


def __readBonus_outfits(bonus, _name, section):
    outfits = {}
    for seasonTypeName, seasonTypeID in {'winter': SeasonType.WINTER,
     'summer': SeasonType.SUMMER,
     'desert': SeasonType.DESERT,
     'event': SeasonType.EVENT}.iteritems():
        if section.has_key(seasonTypeName):
            outfits[seasonTypeID] = section[seasonTypeName].asString.decode('base64')

    bonus['outfits'] = outfits


def __readBonus_customizations(bonus, _name, section, eventType, checkLimit):
    lst = []
    for subsection in section.values():
        custData = {'value': subsection.readInt('value', 0),
         'custType': subsection.readString('custType', ''),
         'id': subsection.readInt('id', -1)}
        if subsection.has_key('boundVehicle'):
            custData['vehTypeCompDescr'] = vehicles.makeIntCompactDescrByID('vehicle', *vehicles.g_list.getIDsByName(subsection.readString('boundVehicle', '')))
        elif subsection.has_key('boundToCurrentVehicle'):
            if eventType in EVENT_TYPE.LIKE_TOKEN_QUESTS:
                raise SoftException("Unsupported tag 'boundToCurrentVehicle' in 'like token' quests")
            custData['boundToCurrentVehicle'] = True
        if subsection.has_key('customCompensation'):
            __readBonus_customCompensation(custData, None, subsection['customCompensation'])
        if subsection.has_key('serialNumberSequence'):
            custData['serialNumberSequence'] = subsection.readString('serialNumberSequence', '')
        isValid, item = validateCustomizationItem(custData)
        if not isValid:
            raise SoftException(item)
        lst.append(custData)

    bonus['customizations'] = lst
    return


def __readBonus_crewSkin(bonus, _name, section, eventType, checkLimit):
    crewSkinID = section.readInt('id', NO_CREW_SKIN_ID)
    skinData = {'id': crewSkinID,
     'count': section.readInt('count', 0)}
    if crewSkinID not in tankmen.g_cache.crewSkins().skins:
        raise SoftException("Unknown crew skin id '%s'" % crewSkinID)
    if skinData['count'] == 0:
        raise SoftException("Invalid count for crew skin id '%s'" % crewSkinID)
    if checkLimit and skinData['count'] > INVOICE_LIMITS.CREW_SKINS:
        raise SoftException('Invalid count of crew skin id %s with amount %d when limit is %d.' % (crewSkinID, skinData['count'], INVOICE_LIMITS.CREW_SKINS))
    bonus.setdefault('crewSkins', []).append(skinData)


def __readBonus_tokens(bonus, _name, section, eventType, checkLimit):
    tokenID = section['id'].asString
    checkLogExtInfoLen(tokenID, 'token')
    if tokenID.startswith(tankmen.RECRUIT_TMAN_TOKEN_PREFIX) and tankmen.getRecruitInfoFromToken(tokenID) is None:
        raise SoftException('Invalid tankman token format: {}'.format(tokenID))
    token = bonus.setdefault('tokens', {})[tokenID] = {}
    expires = token.setdefault('expires', {})
    __readBonus_expires(tokenID, expires, section)
    if section.has_key('limit'):
        token['limit'] = section['limit'].asInt
    token['count'] = 1
    if section.has_key('count'):
        token['count'] = section['count'].asInt
    res = validateCustomizationQuestToken(tokenID, token)
    if not res[0]:
        raise SoftException(res[1])
    if checkLimit and token['count'] > INVOICE_LIMITS.TOKENS_MAX:
        raise SoftException('Invalid count of tankman token with id %s with amount %d when limit is %d.' % (tokenID, token['count'], INVOICE_LIMITS.TOKENS_MAX))
    return


def __readBonus_goodies(bonus, _name, section, eventType, checkLimit):
    goodieID = section['id'].asInt
    goodies = bonus.setdefault('goodies', {})
    if goodieID in goodies:
        raise SoftException('Duplicated goodie with id {}'.format(goodieID))
    goodie = goodies.setdefault(goodieID, {})
    if section.has_key('limit'):
        goodie['limit'] = max(goodie.get('limit', 0), section['limit'].asInt)
    if section.has_key('count'):
        goodie['count'] = __readIntWithTokenExpansion(section['count'])
    else:
        goodie['count'] = 1
    if checkLimit and goodie['count'] > INVOICE_LIMITS.GOODIES_MAX:
        raise SoftException('Invalid count for goodie with id %d with amount %d when limit is %d.' % (goodieID, goodie['count'], INVOICE_LIMITS.GOODIES_MAX))


def __readBonus_enhancement(bonus, _name, section, eventType, checkLimit):
    enhancementID = section.asInt
    count = 1
    wipe = False
    if section.has_key('count'):
        count = section['count'].asInt
    if section.has_key('wipe'):
        wipe = section['wipe'].asBool
    bonus.setdefault('enhancements', {})[enhancementID] = {'count': count,
     'wipe': wipe}


def __readBonus_entitlement(bonus, _name, section, eventType, checkLimit):
    entID, entData = _readEntitlementSection(section, checkLimit)
    bonus.setdefault('entitlements', {})[entID] = entData


def __readBonus_entitlementList(bonus, _name, section, eventType, checkLimit):
    entItems = bonus.setdefault('entitlementList', {}).setdefault('items', [])
    for name, itemSection in section.items():
        if name != 'item':
            raise SoftException('Not expected element', name)
        entID, entData = _readEntitlementSection(itemSection, checkLimit, readOp=True)
        if entData['count'] <= 0:
            raise SoftException('Not positive count for entitlement with operation', entID, entData)
        entData['id'] = entID
        entItems.append(entData)


def _readEntitlementSection(section, checkLimit, readOp=False):
    entitlement = {}
    entID = section['id'].asString
    checkLogExtInfoLen(entID, 'entitlement')
    if section.has_key('count'):
        entitlement['count'] = section['count'].asInt
    else:
        entitlement['count'] = 1
    if readOp:
        entitlement['op'] = operation = section.readString('operation', '')
        if operation not in ENTITLEMENT_OPS.ALL:
            raise SoftException('Invalid op for entitlement:', entID, operation, ENTITLEMENT_OPS.ALL)
    if checkLimit and entitlement['count'] > INVOICE_LIMITS.ENTITLEMENTS_MAX:
        raise SoftException('Invalid count of entitlement id %s with amount %d when limit is %d.' % (entID, entitlement['count'], INVOICE_LIMITS.ENTITLEMENTS_MAX))
    if section.has_key('expires'):
        entitlement['expires'] = expires = {}
        __readBonus_expires(entID, expires, section)
    return (entID, entitlement)


def __readBonus_currency(bonus, _name, section, eventType, checkLimit):
    currencyCode = section['code'].asString
    if not g_dynamicCurrenciesData.isCurrencyCodeCorrect(currencyCode):
        raise SoftException('Incorrect code "%(code)s" has been provided in section <currency> in quests xml - it does not exist at platform.' % {'code': currencyCode})
    currency = bonus.setdefault('currencies', {})[currencyCode] = {}
    currency['count'] = section['count'].asInt


def __readBonus_expires(bonusID, expires, section):
    if section['expires'].has_key('endOfGameDay'):
        expires['endOfGameDay'] = True
        return
    else:
        if section['expires'].has_key('after'):
            expires['after'] = section['expires']['after'].asInt
        else:
            expires['at'] = readUTC(section, 'expires')
            if expires['at'] is None:
                raise SoftException('Invalid expiry time for %s' % bonusID)
        return


def __readBonus_dossier(bonus, _name, section, eventType, checkLimit):
    blockName, record = section['name'].asString.split(':')
    operation = 'add'
    if section.has_key('type'):
        operation = section['type'].asString
    if operation not in ('add', 'append', 'set'):
        raise SoftException('Invalid dossier record %s' % operation)
    strValue = section['value'].asString
    value = int(strValue) if strValue not in ('timestamp',) else strValue
    unique = False
    if section.has_key('unique'):
        unique = section['unique'].asBool
    dossierType = DOSSIER_TYPE.ACCOUNT
    if section.has_key('dossierType'):
        dossierType = section['dossierType'].asInt
    if dossierType == DOSSIER_TYPE.ACCOUNT:
        if blockName in ACCOUNT_DOSSIER_DICT_BLOCKS:
            try:
                record = int(record)
            except ValueError:
                pass

        isValid, message = checkAccountDossierOperation(dossierType, blockName, record, operation)
        if not isValid:
            raise SoftException('Invalid dossier bonus %s: %s' % (blockName + ':' + record, message))
    else:
        raise SoftException('Dossier type %s not supported in bonus reader' % dossierType)
    bonus.setdefault('dossier', {}).setdefault(dossierType, {})[blockName, record] = {'value': value,
     'unique': unique,
     'type': operation}


def __readBonus_blueprint(bonus, _name, section, eventType, checkLimit):
    bonus.setdefault('blueprints', {})
    compDescr = section.readInt('compDescr', 0) or vehicles.makeVehicleTypeCompDescrByName(section.readString('vehType'))
    if not dossiers2.custom.cache.getCache():
        dossiers2.custom.cache.buildCache()
    cache = dossiers2.custom.cache.getCache()
    if compDescr == 0:
        raise SoftException('Invalid vehicle type name or description %s' % section)
    if not isUniversalFragment(compDescr):
        vehicle = vehicles.getVehicleType(compDescr)
        if compDescr not in cache['vehiclesInTrees']:
            raise SoftException('Invalid vehicle type %s. Vehicle is not in research tree.' % section)
    count = section.readInt('count', 0)
    if checkLimit and count > INVOICE_LIMITS.BLUEPRINTS_MAX:
        raise SoftException('Invalid count of blueprint id %s with amount %d when limit is %d.' % (compDescr, count, INVOICE_LIMITS.BLUEPRINTS_MAX))
    if count != 0:
        bonus['blueprints'].update({compDescr: count})


def __readBonus_blueprintAny(bonus, _name, section, eventType, checkLimit):
    bonus.setdefault('blueprintsAny', {})
    count = section.readInt('count', 1)
    if count < 1:
        raise SoftException('Any blueprint count must be positive, got %s' % count)
    if checkLimit and count > INVOICE_LIMITS.BLUEPRINTS_MAX:
        raise SoftException('Invalid count of any blueprint with amount %d when limit is %d.' % (count, INVOICE_LIMITS.BLUEPRINTS_MAX))
    fragmentType = section.readInt('fragmentType', 1)
    if fragmentType not in [BlueprintTypes.VEHICLE, BlueprintTypes.NATIONAL]:
        raise SoftException('Fragment type should be in range [1, 2], where 1 is Vehicle and 2 is National fragment. Given value is %s' % fragmentType)
    bonus['blueprintsAny'].update({fragmentType: count})


def __readBonus_vehicleChoice(bonus, _name, section, eventType, checkLimit):
    extra = {}
    if section.has_key('levels'):
        for level in section['levels'].asString.split():
            if 1 <= int(level) <= 10:
                extra.setdefault('levels', set()).add(int(level))

    if section.has_key('crewLvl'):
        extra['crewLvl'] = section['crewLvl'].asInt
    bonus['demandedVehicles'] = extra


def __readMetaSection(bonus, _name, section, eventType, checkLimit):
    if section is None:
        return
    else:
        meta = {}
        for local, sub in section.items():
            if local != 'actions':
                meta[local.strip()] = sub.readString('', '').strip()
            meta['actions'] = actions = {}
            for action, params in sub.items():
                actions[action.strip()] = {k.strip():v.readString('', '').strip() for k, v in params.items()}

        bonus['meta'] = meta
        return


def __readBonus_optionalData(config, bonusReaders, section, eventType):
    limitIDs, bonus = __readBonusSubSection(config, bonusReaders, section, eventType)
    probabilityStageCount = config.get('probabilityStageCount', 1)
    probabilitiesList = None
    if section.has_key('probability'):
        probabilities = map(float, section.readString('probability', '').split())
        probabilitiesLen = len(probabilities)
        if probabilitiesLen > probabilityStageCount or probabilitiesLen == 0:
            raise SoftException('Expected {} probabilities, received {}'.format(probabilityStageCount, probabilitiesLen))
        for probability in probabilities:
            if not 0 <= probability <= 100:
                raise SoftException('Probability is out of range: {}'.format(probability))

        probabilitiesList = map(lambda probability: probability / 100.0, probabilities)
        probabilitiesList.extend([probabilitiesList[-1]] * (probabilityStageCount - probabilitiesLen))
    bonusProbability = None
    if section.has_key('bonusProbability'):
        if not config.get('useBonusProbability', False):
            raise SoftException('Redundant option useBonusProbability')
        bonusProbability = section['bonusProbability'].asFloat
        if not 0 <= bonusProbability <= 100:
            raise SoftException('Bonus probability is out of range: {}'.format(bonusProbability))
        bonusProbability /= 100.0
    properties = {}
    if section.has_key('compensation'):
        properties['compensation'] = section['compensation'].asBool
    if section.has_key('shouldCompensated'):
        properties['shouldCompensated'] = section['shouldCompensated'].asBool
    if IS_DEVELOPMENT:
        if section.has_key('name'):
            properties['name'] = section['name'].asString
    if section.has_key('limitID'):
        limitID = section['limitID'].asString
        limitConfig = config.get('limits', {}).get(limitID, {})
        if not limitConfig:
            raise SoftException('Unknown limitID: {}'.format(limitID))
        properties['limitID'] = limitID
        if 'guaranteedFrequency' in limitConfig:
            limitIDs.add(limitID)
    if section.has_key('depthLevel'):
        properties['depthLevel'] = depthLevel = section['depthLevel'].asInt
        if depthLevel < 0:
            raise SoftException("Invalid value for 'checkDepth' option: {}".format(depthLevel))
    if section.has_key('probabilityStageDependence'):
        properties['probabilityStageDependence'] = section['probabilityStageDependence'].asBool
    if properties:
        bonus['properties'] = properties
    return (limitIDs,
     probabilitiesList,
     bonusProbability,
     bonus)


def __readBonus_optional(config, bonusReaders, bonus, section, eventType):
    limitIDs, probabilitiesList, bonusProbability, subBonus = __readBonus_optionalData(config, bonusReaders, section, eventType)
    if probabilitiesList is None:
        raise SoftException("Missing probability attribute in 'optional'")
    if config.get('useBonusProbability', False) and bonusProbability is None:
        raise SoftException("Missing bonusProbability attribute in 'optional'")
    properties = subBonus.get('properties', {})
    for property in ('compensation', 'shouldCompensated', 'depthLevel'):
        if properties.get(property, None) is not None:
            raise SoftException("Property '{}' not allowed for standalone 'optional'".format(property))

    bonus.setdefault('allof', []).append((probabilitiesList,
     bonusProbability,
     limitIDs if limitIDs else None,
     subBonus))
    return limitIDs


def __readBonus_oneof(config, bonusReaders, bonus, section, eventType):
    equalProbabilityCount = 0
    equalBonusProbabilityCount = 0
    oneOfBonus = []
    resultLimitIDs = set()
    useBonusProbability = config.get('useBonusProbability', False)
    probabilityStageCount = config.get('probabilityStageCount', 1)
    equalProbabilityValues = [0.0] * probabilityStageCount
    equalBonusProbabilityValue = 0.0
    for name, subsection in section.items():
        if name != 'optional':
            raise SoftException("Unexpected section (or property) inside 'oneof': {}".format(name))
        limitIDs, probabilitiesList, bonusProbability, subBonus = __readBonus_optionalData(config, bonusReaders, subsection, eventType)
        if probabilitiesList is None:
            equalProbabilityCount += 1
        else:
            for i in xrange(probabilityStageCount):
                equalProbabilityValues[i] += probabilitiesList[i]

        if useBonusProbability:
            if bonusProbability is None:
                equalBonusProbabilityCount += 1
            else:
                equalBonusProbabilityValue += bonusProbability
        if limitIDs:
            if resultLimitIDs:
                raise SoftException('Guaranteed limits conflict', resultLimitIDs, limitIDs)
            limitID = subBonus.get('properties', {}).get('limitID', None)
            if limitID and 'guaranteedFrequency' not in config['limits'][limitID]:
                raise SoftException('Limits conflict', limitID, limitIDs)
            resultLimitIDs.update(limitIDs)
        oneOfBonus.append((probabilitiesList,
         bonusProbability,
         limitIDs if limitIDs else None,
         subBonus))

    if equalProbabilityCount:
        equalProbabilityValues = [ (1.0 - equalProbabilityValue) / equalProbabilityCount for equalProbabilityValue in equalProbabilityValues ]
    if equalBonusProbabilityCount:
        equalBonusProbabilityValue = (1.0 - equalBonusProbabilityValue) / equalBonusProbabilityCount
    oneOfTemp = []
    maximumProbabilities = [0.0] * probabilityStageCount
    maximumBonusProbability = 0.0
    for probabilities, bonusProbability, limitIDs, subBonus in oneOfBonus:
        if probabilities is None:
            probabilitiesList = equalProbabilityValues
        else:
            probabilitiesList = probabilities
        for i in xrange(probabilityStageCount):
            maximumProbabilities[i] += probabilitiesList[i]

        if useBonusProbability:
            if bonusProbability is None:
                maximumBonusProbability += equalBonusProbabilityValue
            else:
                maximumBonusProbability += bonusProbability
        values = maximumProbabilities if probabilities != [0.0] * probabilityStageCount else probabilities
        bonusValue = maximumBonusProbability if bonusProbability != 0.0 and useBonusProbability else bonusProbability
        oneOfTemp.append(([ min(1.0, value) for value in values ],
         min(1.0, bonusValue),
         limitIDs,
         subBonus))

    for maximumProbability in maximumProbabilities:
        if abs(1.0 - maximumProbability) >= 1e-06:
            raise SoftException('Sum of probabilities != 100', maximumProbability)

    if useBonusProbability and abs(1.0 - maximumBonusProbability) >= 1e-06:
        raise SoftException('Sum of bonus probabilities != 100', maximumBonusProbability)
    bonus.setdefault('groups', []).append({'oneof': (resultLimitIDs if resultLimitIDs else None, oneOfTemp)})
    return resultLimitIDs


def __readBonus_dogTag(bonus, _name, section, eventType, checkLimit):
    componentId = section['id'].asInt
    data = {'id': componentId}
    value = section.readFloat('value', 0.0)
    grade = section.readInt('grade', 0)
    unlock = section.readBool('unlock', False)
    needRecalculate = section.readBool('needRecalculate', False)
    if value is not 0.0:
        data['value'] = value
    if grade is not 0:
        data['grade'] = grade
    if unlock is not False:
        data['unlock'] = unlock
    if needRecalculate is not False:
        data['needRecalculate'] = needRecalculate
    bonus.setdefault('dogTagComponents', []).append(data)


def __readBonus_battlePassPoints(bonus, _name, section, eventType, checkLimit):
    count = __readIntWithTokenExpansion(section)
    if checkLimit and count > INVOICE_LIMITS.BATTLE_PASS_POINTS:
        raise SoftException('Invalid count of battlePassPoints with amount %d when limit is %d.' % (count, INVOICE_LIMITS.BATTLE_PASS_POINTS))
    bonus['battlePassPoints'] = {'vehicles': {NON_VEH_CD: count}}


def __readBonus_dailyQuestReroll(bonus, name, section, eventType, checkLimit):
    data = section.asString
    levels = set(data.strip().split())
    if set(levels).intersection(DailyQuestsLevels.ALL) != levels:
        raise SoftException('Invalid daily quest level {}'.format(levels))
    bonus[name] = levels


def __readBonus_noviceReset(bonus, name, section, eventType, checkLimit):
    noviceType = section['noviceType'].asInt
    noviceRating = section['noviceRating'].asInt
    bonus[name] = {'noviceType': noviceType,
     'noviceRating': noviceRating}


def __readBonus_freePremiumCrew(bonus, _name, section, eventType, checkLimit):
    vehLevel = section['vehLevel'].asInt
    count = section.readInt('count', 1)
    if 'freePremiumCrew' in bonus and vehLevel in bonus['freePremiumCrew']:
        raise SoftException('Duplicate free premium crew vehLevel', vehLevel)
    freePremiumCrewBonus = bonus.setdefault('freePremiumCrew', {})
    freePremiumCrewBonus[vehLevel] = count


def __readBonus_group(config, bonusReaders, bonus, section, eventType):
    limitIDs, subBonus = __readBonusSubSection(config, bonusReaders, section, eventType)
    bonus.setdefault('groups', []).append(subBonus)
    return limitIDs


__BONUS_READERS = {'meta': __readMetaSection,
 'buyAllVehicles': __readBonus_bool,
 'buySecretVehicles': __readBonus_bool,
 'buySpecialVehicles': __readBonus_bool,
 'buyCommonVehicles': __readBonus_bool,
 'researchAllVehicles': __readBonus_bool,
 'equipGold': __readBonus_bool,
 'ultimateLoginPriority': __readBonus_bool,
 'addTankmanSkills': __readBonus_bool,
 'buySpecial': __readBonus_string_set,
 'premiumAmmo': __readBonus_int,
 'gold': bonusReaderLimitDecorator(INVOICE_LIMITS.GOLD_MAX, __readBonus_int),
 'credits': bonusReaderLimitDecorator(INVOICE_LIMITS.CREDITS_MAX, __readBonus_int),
 'crystal': bonusReaderLimitDecorator(INVOICE_LIMITS.CRYSTAL_MAX, __readBonus_int),
 'eventCoin': bonusReaderLimitDecorator(INVOICE_LIMITS.EVENT_COIN_MAX, __readBonus_int),
 'bpcoin': bonusReaderLimitDecorator(INVOICE_LIMITS.BPCOIN_MAX, __readBonus_int),
 'equipCoin': bonusReaderLimitDecorator(INVOICE_LIMITS.EQUIP_COIN_MAX, __readBonus_int),
 'freeXP': bonusReaderLimitDecorator(INVOICE_LIMITS.FREEXP_MAX, __readBonus_int),
 'slots': bonusReaderLimitDecorator(INVOICE_LIMITS.SLOTS_MAX, __readBonus_int),
 'berths': bonusReaderLimitDecorator(INVOICE_LIMITS.BERTHS_MAX, __readBonus_int),
 'premium': __readBonus_int,
 'premium_plus': __readBonus_int,
 'premium_vip': __readBonus_int,
 'xp': __readBonus_int,
 'tankmenXP': __readBonus_int,
 'vehicleXP': __readBonus_int,
 'trainCommander': __readBonus_int,
 'maxVehicleLevel': __readBonus_int,
 'xpFactor': __readBonus_factor,
 'creditsFactor': __readBonus_factor,
 'freeXPFactor': __readBonus_factor,
 'tankmenXPFactor': __readBonus_factor,
 'vehicleXPFactor': __readBonus_factor,
 'item': __readBonus_item,
 'enhancement': __readBonus_enhancement,
 'equipment': __readBonus_equipment,
 'optionalDevice': __readBonus_optionalDevice,
 'token': __readBonus_tokens,
 'goodie': __readBonus_goodies,
 'vehicle': __readBonus_vehicle,
 'dossier': __readBonus_dossier,
 'tankmen': __readBonus_tankmen,
 'customizations': __readBonus_customizations,
 'crewSkin': __readBonus_crewSkin,
 'entitlement': __readBonus_entitlement,
 'entitlementList': __readBonus_entitlementList,
 'rankedDailyBattles': bonusReaderLimitDecorator(INVOICE_LIMITS.RANKED_DAILY_BATTLES_MAX, __readBonus_int),
 'rankedBonusBattles': bonusReaderLimitDecorator(INVOICE_LIMITS.RANKED_BONUS_BATTLES_MAX, __readBonus_int),
 'dogTagComponent': __readBonus_dogTag,
 'battlePassPoints': __readBonus_battlePassPoints,
 'dailyQuestReroll': __readBonus_dailyQuestReroll,
 'noviceReset': __readBonus_noviceReset,
 'vehicleChoice': __readBonus_vehicleChoice,
 'blueprint': __readBonus_blueprint,
 'blueprintAny': __readBonus_blueprintAny,
 'currency': __readBonus_currency,
 'freePremiumCrew': __readBonus_freePremiumCrew}
__PROBABILITY_READERS = {'optional': __readBonus_optional,
 'oneof': __readBonus_oneof,
 'group': __readBonus_group}
_RESERVED_NAMES = frozenset(['config',
 'properties',
 'limitID',
 'probability',
 'compensation',
 'name',
 'shouldCompensated',
 'probabilityStageDependence',
 'bonusProbability',
 'depthLevel'])
SUPPORTED_BONUSES = frozenset(__BONUS_READERS.iterkeys())
__SORTED_BONUSES = sorted(SUPPORTED_BONUSES)
SUPPORTED_BONUSES_IDS = dict(((n, i) for i, n in enumerate(__SORTED_BONUSES)))
SUPPORTED_BONUSES_NAMES = {i:n for i, n in enumerate(__SORTED_BONUSES)}

def __readBonusLimit(section):
    properties = {}
    name = section.readString('name', '')
    if not name:
        raise SoftException('Limit name missing')
    for property in ('maxFrequency', 'guaranteedFrequency', 'bonusLimit', 'useBonusProbabilityAfter'):
        value = section[property]
        if value is not None:
            properties[property] = value.asInt

    for property in ('countDuplicates', 'isForPlayers'):
        value = section[property]
        if value is not None:
            properties[property] = value.asBool

    if not properties:
        raise SoftException('Empty limit section: {}'.format(name))
    if sum((True for property in properties if property in ('maxFrequency', 'guaranteedFrequency', 'bonusLimit', 'useBonusProbabilityAfter'))) > 1:
        raise SoftException('Too many limits: {}'.format(name))
    return (name, properties)


def __readBonusConfig(section):
    config = {}
    for name, data in section.items():
        if name == 'limit':
            limits = config.setdefault('limits', {})
            limitName, limitConfig = __readBonusLimit(data)
            if limitName in limits:
                raise SoftException('Bonus limit already defined: {}'.format(limitName))
            limits[limitName] = limitConfig
        if name == 'needsBonusExpansion':
            config.setdefault('needsBonusExpansion', False)
            config['needsBonusExpansion'] = data.asBool
        if name == 'probabilityStageCount':
            config.setdefault('probabilityStageCount', 1)
            probabilityStageCount = data.asInt
            if probabilityStageCount < 1:
                raise SoftException('Invalid probabilityStageCount value {}, expected greater or equal 1'.format(probabilityStageCount))
            config['probabilityStageCount'] = probabilityStageCount
        if name == 'useBonusProbability':
            config.setdefault('useBonusProbability', False)
            config['useBonusProbability'] = data.asBool
        if name == 'showBonusInfo':
            config['showBonusInfo'] = data.asBool
        if name == 'showProbabilitiesInfo':
            config['showProbabilitiesInfo'] = data.asBool
        raise SoftException('Unknown config section: {}'.format(name))

    limitIDsLen = sum([ len(limitID) for limitID in config.get('limits', {}) ])
    if limitIDsLen > 200:
        raise SoftException('Limit IDs (len = {}) might not fit to token len ({}) for logging purposes'.format(limitIDsLen, MAX_LOG_EXT_INFO_LEN))
    return config


def readBonusSection(bonusRange, section, eventType=None, checkLimit=True):
    if section is None:
        return {}
    else:
        bonusReaders = getBonusReaders(bonusRange)
        config = __readBonusConfig(section['config']) if section.has_key('config') else {}
        limitIDs, bonus = __readBonusSubSection(config, bonusReaders, section, eventType, checkLimit)
        if config:
            bonus['config'] = config
        return bonus


def __readBonusSubSection(config, bonusReaders, section, eventType=None, checkLimit=True):
    bonus = {}
    resultLimitIDs = set()
    for name, subSection in section.items():
        if name in __PROBABILITY_READERS:
            limitIDs = __PROBABILITY_READERS[name](config, bonusReaders, bonus, subSection, eventType)
            if limitIDs:
                resultLimitIDs.update(limitIDs)
        if name in bonusReaders:
            bonusReaders[name](bonus, name, subSection, eventType, checkLimit)
        if name in _RESERVED_NAMES:
            pass
        raise SoftException('Bonus {} not in bonus readers: {}'.format(name, bonusReaders.keys()))

    return (resultLimitIDs, bonus)
