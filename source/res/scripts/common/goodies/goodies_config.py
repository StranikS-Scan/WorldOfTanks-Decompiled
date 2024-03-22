# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/goodies_config.py
import time
import calendar
import datetime
import XmlConfigReader
import helpers_common
from debug_utils import LOG_WARNING
from goodie_constants import GOODIE_VARIETY
from . import goodie_helpers
from items.vehicles import makeVehicleTypeCompDescrByName
from soft_exception import SoftException
_CONFIG_FILE = 'scripts/server_xml/goodies.xml'
g_cache = None

def readConfig(verbose):
    reader = XmlConfigReader.makeReader(_CONFIG_FILE, 'goodies', verbose)
    return _readGoodies(reader, 'goodies')


def _readGoodieResource(section):
    for n, t in goodie_helpers.GOODIE_TEXT_TO_RESOURCE.iteritems():
        v = section.readString(n, '')
        if v:
            value, isPercentage = XmlConfigReader.parsePercentage(v)
            return (t, value, isPercentage)

    raise SoftException('Goodie without any resources')


def _readGoodieTarget(reader, subsectionName):
    for n, t in goodie_helpers.GOODIE_TEXT_TO_TARGET.iteritems():
        section = reader.getSubsection('/'.join((subsectionName, n)))
        if section:
            name = section.readString('name', '')
            if name == '':
                name = None
            if name and t == goodie_helpers.GOODIE_TARGET_TYPE.ON_BUY_VEHICLE:
                name = makeVehicleTypeCompDescrByName(name)
            limit = section.readInt('limit', 0)
            if limit == 0:
                limit = None
            resource = _readGoodieResource(section)
            return ((t, name, limit), resource)

    return


def _readGoodieCondition(section):
    if section is None:
        return
    else:
        for n, t in goodie_helpers.GOODIE_TEXT_TO_CONDITION.iteritems():
            value = section.readString(n, '')
            if value:
                return (t, int(value))

        return


def _readPrice(reader, subsectionName):
    priceSectionName = subsectionName + '/price'
    if reader.getSubsection(priceSectionName) is None:
        return
    else:
        if reader.getSubsection(priceSectionName + '/gold') is not None:
            isGold = True
        else:
            isGold = False
        value = reader.getSubsection(subsectionName).readInt('price', 0)
        if isGold:
            return (0, value)
        return (value, 0)
        return


def _validator(uid, variety, resource, price):
    t, value, isPercentage = resource
    if value < 0:
        raise SoftException('Bad goodie %d value (negative) %d' % uid % value)
    if variety in GOODIE_VARIETY.DISCOUNT_LIKE and isPercentage and value > 100:
        raise SoftException('Bad goodie %d value %d' % uid % value)
    if price is not None and price <= 0:
        raise SoftException('Bad goodie %d price (negative or zero) %d' % uid % price)
    return


def _readGoodies(reader, subsectionName):
    section = reader.getSubsection(subsectionName)
    if section is None:
        return {}
    else:
        goodies = {'goodies': {},
         'prices': {},
         'notInShop': set()}
        for packet_name, packet in section.items():
            v, uid = (None, -1)
            if '_' in packet_name:
                v, uid = packet_name.split('_')
            variety = GOODIE_VARIETY.NAME_TO_ID.get(v, None)
            if variety is None:
                raise SoftException('No <%s> parameter' % 'variety')
            uid = int(uid)
            if uid < 0:
                raise SoftException('No <uid> parameter')
            enabled = bool(packet.readInt('enabled', 1))
            autostart = bool(packet.readInt('autostart', 0))
            notInShop = bool(packet.readInt('notInShop', 1))
            counter = packet.readInt('counter', 1)
            expireAfter = helpers_common.parseDuration(packet.readString('expireAfter', '0'))
            if expireAfter == 0:
                expireAfter = None
            roundToEndOfGameDay = packet.readBool('roundToEndOfGameDay', True)
            lifetime = helpers_common.parseDuration(packet.readString('lifetime', '0'))
            if lifetime == 0:
                lifetime = None
            useby = packet.readString('useby', '')
            if useby == '':
                useby = None
            else:
                useby = calendar.timegm(datetime.datetime.strptime(useby, '%d.%m.%Y %H:%M:%S').timetuple())
            condition = _readGoodieCondition(reader.getSubsection('/'.join((subsectionName, packet_name, 'condition'))))
            target, resource = _readGoodieTarget(reader, '/'.join((subsectionName, packet_name)))
            price = _readPrice(reader, '/'.join((subsectionName, packet_name)))
            _validator(uid, variety, resource, price)
            goodies['goodies'][uid] = (variety,
             target,
             enabled,
             lifetime,
             useby,
             counter,
             autostart,
             condition,
             resource,
             expireAfter,
             roundToEndOfGameDay)
            if price is not None:
                goodies['prices'][uid] = price
            if notInShop or price is None:
                goodies['notInShop'].add(uid)
            if useby is not None and useby < time.time():
                LOG_WARNING('Expired goodie is removed from the shop %d' % uid)
                goodies['notInShop'].add(uid)

        return goodies


def init(gameParams=None):
    global g_cache
    if gameParams is not None:
        goodies = gameParams['goodies']
    else:
        goodies = readConfig(True)
    if g_cache is None:
        g_cache = {}
    else:
        g_cache.clear()
    g_cache.update(goodie_helpers.loadDefinitions(goodies))
    return
