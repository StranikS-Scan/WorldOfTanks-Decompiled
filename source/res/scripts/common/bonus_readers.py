# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/bonus_readers.py
import time
import items
import calendar
from account_shared import validateCustomizationItem
from invoices_helpers import checkAccountDossierOperation
from items import vehicles, tankmen, festival
from items.components.c11n_constants import SeasonType
from items.components.crew_skins_constants import NO_CREW_SKIN_ID
from constants import DOSSIER_TYPE, IS_DEVELOPMENT, SEASON_TYPE_BY_NAME, EVENT_TYPE
from soft_exception import SoftException
__all__ = ['readBonusSection', 'readUTC', 'SUPPORTED_BONUSES']

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


def __readBonus_bool(bonus, name, section, eventType):
    bonus[name] = section.asBool


def __readBonus_string_set(bonus, name, section, eventType):
    data = section.asString
    bonus[name] = data.strip().split()


def __readBonus_int(bonus, name, section, eventType):
    value = section.asInt
    if value < 0:
        raise SoftException('Negative value (%s)' % name)
    bonus[name] = section.asInt


def __readBonus_factor(bonus, name, section, eventType):
    value = section.asFloat
    if value < 0:
        raise SoftException('Negative value (%s)' % name)
    bonus[name] = value


def __readBonus_equipment(bonus, _name, section, eventType):
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


def __readBonus_optionalDevice(bonus, _name, section, eventType):
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


def __readBonus_item(bonus, _name, section, eventType):
    compDescr = section.asInt
    try:
        itemTypeID, _, _ = vehicles.parseIntCompactDescr(compDescr)
        itemsCache = vehicles if itemTypeID in vehicles.VEHICLE_ITEM_TYPES else tankmen
        descr = itemsCache.getItemByCompactDescr(compDescr)
        if descr.itemTypeName not in items.SIMPLE_ITEM_TYPE_NAMES:
            raise SoftException('Wrong compact descriptor (%d). Not simple item.' % compDescr)
    except:
        raise SoftException('Wrong compact descriptor (%d)' % compDescr)

    count = 1
    if section.has_key('count'):
        count = section['count'].asInt
    bonus.setdefault('items', {})[compDescr] = count


def __readBonus_vehicle(bonus, _name, section, eventType):
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
        __readBonus_tankmen(extra, vehTypeCompDescr, section['tankmen'], eventType)
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
    if section.has_key('ammo'):
        ammo = section['ammo'].asString
        extra['ammo'] = [ int(item) for item in ammo.split(' ') ]
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


def __readBonus_tankmen(bonus, vehTypeCompDescr, section, eventType):
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


def __readBonus_customizations(bonus, _name, section, eventType):
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
        isValid, item = validateCustomizationItem(custData)
        if not isValid:
            raise SoftException(item)
        lst.append(custData)

    bonus['customizations'] = lst
    return


def __readBonus_crewSkin(bonus, _name, section, eventType):
    crewSkinID = section.readInt('id', NO_CREW_SKIN_ID)
    skinData = {'id': crewSkinID,
     'count': section.readInt('count', 0)}
    if crewSkinID not in tankmen.g_cache.crewSkins().skins:
        raise SoftException("Unknown crew skin id '%s'" % crewSkinID)
    if skinData['count'] == 0:
        raise SoftException("Invalid count for crew skin id '%s'" % crewSkinID)
    bonus.setdefault('crewSkins', []).append(skinData)


def __readBonus_tokens(bonus, _name, section, eventType):
    id = section['id'].asString
    if id.startswith(tankmen.RECRUIT_TMAN_TOKEN_PREFIX) and tankmen.getRecruitInfoFromToken(id) is None:
        raise SoftException('Invalid tankman token format: {}'.format(id))
    token = bonus.setdefault('tokens', {})[id] = {}
    expires = token.setdefault('expires', {})
    __readBonus_expires(id, expires, section)
    if section.has_key('limit'):
        token['limit'] = section['limit'].asInt
    token['count'] = 1
    if section.has_key('count'):
        token['count'] = section['count'].asInt
    return


def __readBonus_goodies(bonus, _name, section, eventType):
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


def __readBonus_dossier(bonus, _name, section, eventType):
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


def __readBonus_blueprint(bonus, _name, section, eventType):
    bonus.setdefault('blueprints', {})
    compDescr = section.readInt('compDescr', 0) or vehicles.makeVehicleTypeCompDescrByName(section.readString('vehType'))
    if compDescr == 0:
        raise SoftException('Invalid vehicle type name or description %s' % section)
    count = section.readInt('count', 0)
    if count != 0:
        bonus['blueprints'].update({compDescr: count})


def __readBonus_blueprintAny(bonus, _name, section, eventType):
    bonus.setdefault('blueprintsAny', {})
    nationID = section.readInt('nationID', -1)
    level = section.readInt('level', -1)
    if not (level == -1 or 1 < level < 11):
        raise SoftException('Invalid vehicle level %s, must be [2..10] or missing' % level)
    vehClass = section.readString('vehClass', 'any')
    if not (vehClass == 'any' or vehClass in vehicles.VEHICLE_CLASS_TAGS):
        raise SoftException('Invalid vehicle class %s' % vehClass)
    count = section.readInt('count', 1)
    if count < 1:
        raise SoftException('Any blueprint count must be positive, got %s' % count)
    bonus['blueprintsAny'].update({(nationID, vehClass, level): count})


def __readBonus_vehicleChoice(bonus, _name, section, eventType):
    extra = {}
    if section.has_key('levels'):
        for level in section['levels'].asString.split():
            if 1 <= int(level) <= 10:
                extra.setdefault('levels', set()).add(int(level))

    bonus['demandedVehicles'] = extra


def __readBonus_festivalItem(bonus, _name, section, eventType):
    if section.has_key('id'):
        itemID = section['id'].asInt
        if itemID not in festival.g_cache.getCollection():
            raise SoftException('Unknown festival item ID: %d' % itemID)
        count = 1
        if section.has_key('count'):
            count = section['count'].asInt
        festivalItems = bonus.setdefault('festivalItems', {})
        festivalItems[itemID] = festivalItems.get(itemID, 0) + count


def __readMetaSection(bonus, _name, section, eventType):
    if section is None:
        return
    else:
        meta = {}
        for local, sub in section.items():
            meta[local.strip()] = sub.readString('', '').strip()

        bonus['meta'] = meta
        return


def __readBonus_optionalData(config, bonusReaders, section, eventType):
    limitIDs, bonus = __readBonusSubSection(config, bonusReaders, section, eventType)
    probability = section['probability']
    if probability is not None:
        probability = probability.asFloat
        if not 0 <= probability <= 100:
            raise SoftException('Probability is out of range: {}'.format(probability))
        probability = probability / 100.0
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
    if properties:
        bonus['properties'] = properties
    return (limitIDs, probability, bonus)


def __readBonus_optional(config, bonusReaders, bonus, section, eventType):
    limitIDs, probability, subBonus = __readBonus_optionalData(config, bonusReaders, section, eventType)
    if probability is None:
        raise SoftException("Missing probability attribute in 'optional'")
    properties = subBonus.get('properties', {})
    for property in ('compensation', 'shouldCompensated'):
        if properties.get(property, None) is not None:
            raise SoftException("Property '{}' not allowed for standalone 'optional'".format(property))

    bonus.setdefault('allof', []).append((probability, limitIDs if limitIDs else None, subBonus))
    return limitIDs


def __readBonus_oneof(config, bonusReaders, bonus, section, eventType):
    equalProbabilityCount = 0
    equalProbabilityValue = 0
    oneOfBonus = []
    resultLimitIDs = set()
    for name, subsection in section.items():
        if name != 'optional':
            raise SoftException("Unexpected section (or property) inside 'oneof': {}".format(name))
        limitIDs, probability, subBonus = __readBonus_optionalData(config, bonusReaders, subsection, eventType)
        if probability is None:
            equalProbabilityCount += 1
        else:
            equalProbabilityValue += probability
        if limitIDs:
            if resultLimitIDs:
                raise SoftException('Guaranteed limits conflict', resultLimitIDs, limitIDs)
            limitID = subBonus.get('properties', {}).get('limitID', None)
            if limitID and 'guaranteedFrequency' not in config['limits'][limitID]:
                raise SoftException('Limits conflict', limitID, limitIDs)
            resultLimitIDs.update(limitIDs)
        oneOfBonus.append((probability, limitIDs if limitIDs else None, subBonus))

    if equalProbabilityCount:
        equalProbabilityValue = (1.0 - equalProbabilityValue) / equalProbabilityCount
    oneOfTemp = []
    maximumProbability = 0
    for probability, limitIDs, subBonus in oneOfBonus:
        if probability is None:
            maximumProbability += equalProbabilityValue
        else:
            maximumProbability += probability
        value = maximumProbability if probability != 0.0 else probability
        oneOfTemp.append((min(1.0, value), limitIDs, subBonus))

    if abs(1.0 - maximumProbability) >= 1e-06:
        raise SoftException('Sum of probabilities != 100', maximumProbability)
    bonus.setdefault('groups', []).append({'oneof': (resultLimitIDs if resultLimitIDs else None, oneOfTemp)})
    return resultLimitIDs


def __readBonus_group(config, bonusReaders, bonus, section, eventType):
    limitIDs, subBonus = __readBonusSubSection(config, bonusReaders, section, eventType)
    bonus.setdefault('groups', []).append(subBonus)
    return limitIDs


__BONUS_READERS = {'meta': __readMetaSection,
 'buyAllVehicles': __readBonus_bool,
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
 'equipment': __readBonus_equipment,
 'optionalDevice': __readBonus_optionalDevice,
 'token': __readBonus_tokens,
 'goodie': __readBonus_goodies,
 'vehicle': __readBonus_vehicle,
 'dossier': __readBonus_dossier,
 'tankmen': __readBonus_tankmen,
 'customizations': __readBonus_customizations,
 'crewSkin': __readBonus_crewSkin,
 'vehicleChoice': __readBonus_vehicleChoice,
 'blueprint': __readBonus_blueprint,
 'blueprintAny': __readBonus_blueprintAny,
 'festivalTickets': __readBonus_int,
 'festivalItem': __readBonus_festivalItem}
__PROBABILITY_READERS = {'optional': __readBonus_optional,
 'oneof': __readBonus_oneof,
 'group': __readBonus_group}
_RESERVED_NAMES = frozenset(['config',
 'properties',
 'limitID',
 'probability',
 'compensation',
 'name',
 'shouldCompensated'])
SUPPORTED_BONUSES = frozenset(__BONUS_READERS.iterkeys())

def __readBonusLimit(section):
    properties = {}
    name = section.readString('name', '')
    if not name:
        raise SoftException('Limit name missing')
    for property in ('maxFrequency', 'guaranteedFrequency', 'bonusLimit'):
        value = section[property]
        if value is not None:
            properties[property] = value.asInt

    for property in ('countDuplicates',):
        value = section[property]
        if value is not None:
            properties[property] = value.asBool

    if not properties:
        raise SoftException('Empty limit section: {}'.format(name))
    if sum((True for property in properties if property in ('maxFrequency', 'guaranteedFrequency', 'bonusLimit'))) > 1:
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
        raise SoftException('Unknown config section: {}'.format(name))

    return config


def readBonusSection(bonusRange, section, eventType=None):
    if section is None:
        return {}
    else:
        bonusReaders = getBonusReaders(bonusRange)
        config = __readBonusConfig(section['config']) if section.has_key('config') else {}
        limitIDs, bonus = __readBonusSubSection(config, bonusReaders, section, eventType)
        if config:
            bonus['config'] = config
        return bonus


def __readBonusSubSection(config, bonusReaders, section, eventType=None):
    bonus = {}
    resultLimitIDs = set()
    for name, subSection in section.items():
        if name in __PROBABILITY_READERS:
            limitIDs = __PROBABILITY_READERS[name](config, bonusReaders, bonus, subSection, eventType)
            if limitIDs:
                resultLimitIDs.update(limitIDs)
        if name in bonusReaders:
            bonusReaders[name](bonus, name, subSection, eventType)
        if name in _RESERVED_NAMES:
            pass
        raise SoftException('Bonus {} not in bonus readers: {}'.format(name, bonusReaders.keys()))

    return (resultLimitIDs, bonus)
