# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/bonus_readers.py
import time
import items
import calendar
from account_shared import validateCustomizationItem
from invoices_helpers import checkAccountDossierOperation
from items import vehicles, tankmen
from items.components.c11n_constants import SeasonType
from constants import EVENT_TYPE, DOSSIER_TYPE, IS_DEVELOPMENT
from soft_exception import SoftException
__all__ = ['getBonusReaders', 'readUTC', 'SUPPORTED_BONUSES']

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


def __readBonus_bool(bonus, name, section):
    bonus[name] = section.asBool


def __readBonus_string_set(bonus, name, section):
    data = section.asString
    bonus[name] = data.strip().split()


def __readBonus_int(bonus, name, section):
    value = section.asInt
    if value < 0:
        raise SoftException('Negative value (%s)' % name)
    bonus[name] = section.asInt


def __readBonus_factor(bonus, name, section):
    value = section.asFloat
    if value < 0:
        raise SoftException('Negative value (%s)' % name)
    bonus[name] = value


def __readBonus_equipment(bonus, _name, section):
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


def __readBonus_optionalDevice(bonus, _name, section):
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


def __readBonus_item(bonus, _name, section):
    compDescr = section.asInt
    try:
        descr = vehicles.getItemByCompactDescr(compDescr)
        if descr.itemTypeName not in items.SIMPLE_ITEM_TYPE_NAMES:
            raise SoftException('Wrong compact descriptor (%d). Not simple item.' % compDescr)
    except:
        raise SoftException('Wrong compact descriptor (%d)' % compDescr)

    count = 1
    if section.has_key('count'):
        count = section['count'].asInt
    bonus.setdefault('items', {})[compDescr] = count


def __readBonus_vehicle(bonus, _name, section):
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
        __readBonus_tankmen(extra, vehTypeCompDescr, section['tankmen'])
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
    if section.has_key('outfits'):
        __readBonus_outfits(extra, None, section['outfits'])
    bonus.setdefault('vehicles', {})[vehCompDescr if vehCompDescr else vehTypeCompDescr] = extra
    return


def __readBonus_customCompensation(bonus, _name, section):
    credits = section.readInt('credits', 0)
    gold = section.readInt('gold', 0)
    bonus['customCompensation'] = (credits, gold)


def __readBonus_vehicleCustomizations(bonus, _name, section):
    custData = {'value': 1,
     'custType': 'style',
     'id': section.readInt('styleId', -1)}
    if section.has_key('customCompensation'):
        __readBonus_customCompensation(custData, None, section['customCompensation'])
    isValid, item = validateCustomizationItem(custData)
    if not isValid:
        raise SoftException(item)
    bonus['customization'] = {'styleId': custData['id'],
     'customCompensation': custData['customCompensation']}
    return


def __readBonus_tankmen(bonus, vehTypeCompDescr, section):
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
         'roleLevel': subsection.readInt('roleLevel', 50),
         'freeXP': subsection.readInt('freeXP', 0),
         'fnGroupID': subsection.readInt('fnGroupID', 0),
         'lnGroupID': subsection.readInt('lnGroupID', 0),
         'iGroupID': subsection.readInt('iGroupID', 0),
         'isPremium': subsection.readBool('isPremium', False),
         'nationID': subsection.readInt('nationID', -1),
         'vehicleTypeID': subsection.readInt('vehicleTypeID', -1),
         'skills': subsection.readString('skills', '').split(),
         'freeSkills': subsection.readString('freeSkills', '').split()}
        for record in ('firstNameID', 'lastNameID', 'iconID'):
            if tmanData[record] == -1:
                tmanData[record] = None

        try:
            if type(vehTypeCompDescr) == int:
                _, vehNationID, vehicleTypeID = vehicles.parseIntCompactDescr(vehTypeCompDescr)
                if vehNationID != tmanData['nationID'] or vehicleTypeID != tmanData['vehicleTypeID']:
                    raise SoftException('Vehicle and tankman mismatch.')
            lst.append(tmanData)
        except Exception as e:
            raise SoftException('%s: %s' % (e, tmanData))

    bonus['tankmen'] = lst
    return


def __readBonus_rent(bonus, _name, section):
    rent = {}
    if section.has_key('time'):
        rent['time'] = section['time'].asFloat
    if section.has_key('battles'):
        rent['battles'] = section['battles'].asInt
    if section.has_key('wins'):
        rent['wins'] = section['wins'].asInt
    if section.has_key('compensation'):
        credits = section['compensation'].readInt('credits', 0)
        gold = section['compensation'].readInt('gold', 0)
        rent['compensation'] = (credits, gold)
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


def __readBonus_customizations(bonus, _name, section):
    lst = []
    for subsection in section.values():
        custData = {'value': subsection.readInt('value', 0),
         'custType': subsection.readString('custType', ''),
         'id': subsection.readInt('id', -1)}
        if subsection.has_key('boundVehicle'):
            custData['vehTypeCompDescr'] = vehicles.makeIntCompactDescrByID('vehicle', *vehicles.g_list.getIDsByName(subsection.readString('boundVehicle', '')))
        elif subsection.has_key('boundToCurrentVehicle'):
            custData['boundToCurrentVehicle'] = True
        if subsection.has_key('customCompensation'):
            __readBonus_customCompensation(custData, None, subsection['customCompensation'])
        isValid, item = validateCustomizationItem(custData)
        if not isValid:
            raise SoftException(item)
        lst.append(custData)

    bonus['customizations'] = lst
    return


def __readBonus_tokens(bonus, _name, section):
    id = section['id'].asString
    token = bonus.setdefault('tokens', {})[id] = {}
    expires = token.setdefault('expires', {})
    __readBonus_expires(id, expires, section)
    if section.has_key('limit'):
        token['limit'] = section['limit'].asInt
    token['count'] = 1
    if section.has_key('count'):
        token['count'] = section['count'].asInt


def __readBonus_goodies(bonus, _name, section):
    id = section['id'].asInt
    goodie = bonus.setdefault('goodies', {})[id] = {}
    if section.has_key('limit'):
        goodie['limit'] = section['limit'].asInt
    if section.has_key('count'):
        goodie['count'] = section['count'].asInt
    else:
        goodie['count'] = 1


def __readBonus_expires(id, expires, section):
    if section['expires'].has_key('endOfGameDay'):
        expires['endOfGameDay'] = True
        return
    else:
        if section['expires'].has_key('after'):
            expires['after'] = section['expires']['after'].asInt
        else:
            expires['at'] = readUTC(section, 'expires')
            if expires['at'] is None:
                raise SoftException('Invalid expiry time for %s' % id)
        return


def __readBonus_dossier(bonus, _name, section):
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
        isValid, message = checkAccountDossierOperation(dossierType, blockName, record, operation)
        if not isValid:
            raise SoftException('Invalid dossier bonus %s: %s' % (blockName + ':' + record, message))
    else:
        raise SoftException('Dossier type %s not supported in bonus reader' % dossierType)
    bonus.setdefault('dossier', {}).setdefault(dossierType, {})[blockName, record] = {'value': value,
     'unique': unique,
     'type': operation}


def __readBonus_vehicleChoice(bonus, _name, section):
    extra = {}
    if section.has_key('levels'):
        for level in section['levels'].asString.split():
            if 1 <= int(level) <= 10:
                extra.setdefault('levels', set()).add(int(level))

    bonus['demandedVehicles'] = extra


def __readBonus_optional(bonusReaders, bonusRange, bonus, section, hasOneOf, isOneOf):
    subBonus = __readBonusSubSection(bonusReaders, bonusRange, section)
    probabilityAttr = section['probability']
    if not isOneOf and probabilityAttr is None:
        raise SoftException('Missing probability attribute in optional')
    if probabilityAttr is None:
        probability = 0
    else:
        probability = probabilityAttr.asInt / 100.0
    if not 0 <= probability <= 100:
        raise SoftException('Probability is out of range: {}'.format(probability))
    if isOneOf:
        bonus.setdefault('oneof', []).append((probability, subBonus))
    else:
        bonus.setdefault('allof', []).append((probability, subBonus))
    return


def __readBonus_oneof(bonusReaders, bonusRange, bonus, section, hasOneOf, isOneOf):
    equalProbabilityCount = 0
    equalProbabilityValue = 0
    bonuses = __readBonusSubSection(bonusReaders, bonusRange, section, True)
    oneOfBonus = bonuses['oneof']
    for probability, subBonus in oneOfBonus:
        if probability == 0:
            equalProbabilityCount += 1
        equalProbabilityValue += probability

    if equalProbabilityCount:
        equalProbabilityValue = (1.0 - equalProbabilityValue) / equalProbabilityCount
    oneOfTemp = []
    maximumProbability = 0
    for probability, subBonus in oneOfBonus:
        if probability == 0:
            maximumProbability += equalProbabilityValue
        else:
            maximumProbability += probability
        oneOfTemp.append((maximumProbability, subBonus))

    lastProbability, lastSubBonus = oneOfTemp[-1]
    if abs(1.0 - lastProbability) < 1e-06:
        oneOfTemp[-1] = (1.0, lastSubBonus)
    else:
        raise SoftException('Sum of probabilities > 100')
    if hasOneOf:
        bonus.setdefault('groups', []).append({'oneof': oneOfTemp})
    else:
        bonus['oneof'] = oneOfTemp
    return True


def __readBonus_group(bonusReaders, bonusRange, bonus, section, hasOneOf, isOneOf):
    subBonus = __readBonusSubSection(bonusReaders, bonusRange, section)
    bonus.setdefault('groups', []).append(subBonus)


__BONUS_READERS = {'buyAllVehicles': __readBonus_bool,
 'equipGold': __readBonus_bool,
 'ultimateLoginPriority': __readBonus_bool,
 'addTankmanSkills': __readBonus_bool,
 'buySpecial': __readBonus_string_set,
 'premiumAmmo': __readBonus_int,
 'gold': __readBonus_int,
 'credits': __readBonus_int,
 'crystal': __readBonus_int,
 'freeXP': __readBonus_int,
 'slots': __readBonus_int,
 'berths': __readBonus_int,
 'premium': __readBonus_int,
 'xp': __readBonus_int,
 'tankmenXP': __readBonus_int,
 'trainCommander': __readBonus_int,
 'maxVehicleLevel': __readBonus_int,
 'xpFactor': __readBonus_factor,
 'creditsFactor': __readBonus_factor,
 'freeXPFactor': __readBonus_factor,
 'tankmenXPFactor': __readBonus_factor,
 'item': __readBonus_item,
 'equipment': __readBonus_equipment,
 'optionalDevice': __readBonus_optionalDevice,
 'token': __readBonus_tokens,
 'goodie': __readBonus_goodies,
 'vehicle': __readBonus_vehicle,
 'dossier': __readBonus_dossier,
 'tankmen': __readBonus_tankmen,
 'customizations': __readBonus_customizations,
 'vehicleChoice': __readBonus_vehicleChoice}
__PROBABILITY_READERS = {'optional': __readBonus_optional,
 'oneof': __readBonus_oneof,
 'group': __readBonus_group}
SUPPORTED_BONUSES = frozenset(__BONUS_READERS.iterkeys())

def readBonusSection(bonusRange, section, eventType=None):
    if section is None:
        return {}
    else:
        bonusReaders = getBonusReaders(bonusRange)
        bonus = __readBonusSubSection(bonusReaders, bonusRange, section)
        return bonus


def __readMetaSection(section):
    if section is None:
        return {}
    else:
        meta = {}
        for local, sub in section.items():
            meta[local.strip()] = sub.readString('', '').strip()

        return meta


def __readBonusSubSection(bonusReaders, bonusRange, section, isOneOf=False):
    if section is None:
        return {}
    else:
        hasOneOf = False
        bonus = {}
        for name, sub in section.items():
            if isOneOf and name != 'optional' and name != 'name':
                raise SoftException('The only possible subsection of oneof is optional')
            elif name in __PROBABILITY_READERS:
                if __PROBABILITY_READERS[name](bonusReaders, bonusRange, bonus, sub, hasOneOf, isOneOf):
                    hasOneOf = True
                continue
            elif name == 'meta':
                bonus['meta'] = __readMetaSection(sub)
                continue
            elif name == 'name':
                if IS_DEVELOPMENT:
                    bonus['name'] = sub.readString('', '').strip()
                continue
            elif name == 'probability':
                continue
            elif name == 'compensation':
                bonus['compensation'] = sub.readBool('', False)
                continue
            elif name not in bonusReaders:
                raise SoftException('Bonus not in bonus readers {}'.format(name))
            elif bonusRange is not None and name not in bonusRange:
                raise SoftException('Bonus {} is not in the range: ({})'.format(name, bonusRange))
            bonusReaders[name](bonus, name, sub)

        return bonus
