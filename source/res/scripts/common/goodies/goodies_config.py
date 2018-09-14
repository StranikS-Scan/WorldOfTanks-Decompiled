# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/goodies/goodies_config.py
import time
import calendar
import datetime
import XmlConfigReader
from debug_utils import LOG_DEBUG, LOG_WARNING
from . import goodie_constants
from . import goodie_helpers
from items.vehicles import makeVehicleTypeCompDescrByName
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

    raise Exception('Goodie without any resources')


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
        raise Exception('Bad goodie %d value (negative) %d' % uid % value)
    if variety == goodie_constants.GOODIE_VARIETY.DISCOUNT and isPercentage and value > 100:
        raise Exception('Bad goodie %d value %d' % uid % value)
    if price is not None and price <= 0:
        raise Exception('Bad goodie %d price (negative or zero) %d' % uid % price)
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
            if '_' in packet_name:
                v, uid = packet_name.split('_')
            if v == 'discount':
                variety = goodie_constants.GOODIE_VARIETY.DISCOUNT
            elif v == 'booster':
                variety = goodie_constants.GOODIE_VARIETY.BOOSTER
            else:
                raise Exception('No <uid> parameter')
            uid = int(uid)
            if uid < 0:
                raise Exception('No <uid> parameter')
            isEnabled = packet.readInt('enabled', 1)
            if isEnabled == 0:
                enabled = False
            else:
                enabled = True
            isAutostart = packet.readInt('autostart', 0)
            if isAutostart == 0:
                autostart = False
            else:
                autostart = True
            notInShop = packet.readInt('notInShop', 1)
            if notInShop == 0:
                notInShop = False
            else:
                notInShop = True
            counter = packet.readInt('counter', 1)
            lifetime = XmlConfigReader.parseDuration(packet.readString('lifetime', '0'))
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
             resource)
            if price:
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
