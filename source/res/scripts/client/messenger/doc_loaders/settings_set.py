# Embedded file name: scripts/client/messenger/doc_loaders/settings_set.py
from collections import namedtuple
from messenger.doc_loaders import _xml_helpers
from messenger.m_constants import BATTLE_CHANNEL

def _readSet(xmlCtx, section, _, readers):
    result = []
    items = section['items']
    if items is None:
        raise _xml_helpers.XMLError(xmlCtx, 'Items not found')
    for tagName, subSec in items.items():
        if tagName != 'item':
            raise _xml_helpers.XMLError(xmlCtx, 'Tag "{0:>s}" is invalid'.format(tagName))
        ctx = xmlCtx.next(subSec)
        name = _xml_helpers.readNoEmptyStr(xmlCtx, subSec, 'name', 'Item name is not defined')
        if name not in readers:
            raise _xml_helpers.XMLError(xmlCtx, 'Item "{0:>s}" is not valid'.format(name))
        result.append(readers[name](ctx, subSec, settings=None))

    return result


def _readSettings(xmlCtx, section, settings, setReaders, itemReaders):
    for tagName, subSec in section.items():
        if tagName == 'name':
            continue
        if tagName == 'set':
            readers = setReaders
        elif tagName == 'item':
            readers = itemReaders
        else:
            raise _xml_helpers.XMLError(xmlCtx, 'Tag "{0:>s}" is invalid'.format(tagName))
        ctx = xmlCtx.next(subSec)
        name = _xml_helpers.readNoEmptyStr(ctx, subSec, 'name', 'Tag "name" is not defined')
        if name not in readers:
            raise _xml_helpers.XMLError(ctx, 'Set/item "{0:>s}" is not valid'.format(name))
        readers[name](ctx, subSec, settings)


def _readServiceChannel(xmlCtx, section, settings):
    result = dict(_readSet(xmlCtx, section, settings, {'highPriorityMsgLifeTime': _xml_helpers.readFloatItem,
     'highPriorityMsgAlphaSpeed': _xml_helpers.readFloatItem,
     'mediumPriorityMsgLifeTime': _xml_helpers.readFloatItem,
     'mediumPriorityMsgAlphaSpeed': _xml_helpers.readFloatItem,
     'stackLength': _xml_helpers.readIntItem,
     'padding': _xml_helpers.readIntItem}))
    settings.serviceChannel = settings.serviceChannel._replace(**result)


def _readLobbyColors(xmlCtx, section, settings):
    result = dict(_readSet(xmlCtx, section, settings, {'breaker': _xml_helpers.readRGBItem,
     'messageBody': _xml_helpers.readRGBItem,
     'badWord': _xml_helpers.readRGBItem}))
    settings.colors = settings.colors._replace(**result)


_LOBBY_SET_READERS = {'serviceChannel': _readServiceChannel}
_LOBBY_ITEM_READERS = {'messageRawFormat': _xml_helpers.readUnicodeItem,
 'badWordFormat': _xml_helpers.readUnicodeItem}

def _readBattleMessageLifeCycle(xmlCtx, section, settings):
    result = dict(_readSet(xmlCtx, section, settings, {'lifeTime': _xml_helpers.readFloatItem,
     'alphaSpeed': _xml_helpers.readFloatItem}))
    settings.messageLifeCycle = settings.messageLifeCycle._replace(**result)


_ReceiverInBattle = namedtuple('_ReceiverInBattle', ('label', 'modifiers', 'order'))

def _readReceiverValue(xmlCtx, section, settings = None):
    name = _xml_helpers.readNoEmptyStr(xmlCtx, section, 'name', 'Receiver name is not defined')
    valueSec = section['value']
    if not valueSec:
        raise _xml_helpers.XMLError(xmlCtx, 'Item value is not defined')
    modifiers = []
    modifiersSec = valueSec['modifiers']
    if modifiersSec:
        modifiers = map(lambda section: section.asInt, modifiersSec.values())
    label = _xml_helpers.readNoEmptyI18nStr(xmlCtx.next(valueSec), valueSec, 'label', 'Label is not defined')
    return (name, _ReceiverInBattle(label, modifiers, valueSec.readInt('order')))


def _readReceivers(xmlCtx, section, settings):
    readers = {}
    receivers = {}
    for flag, name, label in BATTLE_CHANNEL.ALL:
        readers[name] = _readReceiverValue
        receivers[name] = _ReceiverInBattle(label, [], 0)

    result = dict(_readSet(xmlCtx, section, settings, readers))
    receivers.update(result)
    settings.receivers = receivers


_BATTLE_SET_READERS = {'messageLifeCycle': _readBattleMessageLifeCycle,
 'receivers': _readReceivers}
_BATTLE_ITEM_READERS = {'messageFormat': _xml_helpers.readUnicodeItem,
 'targetFormat': _xml_helpers.readStringItem,
 'inactiveStateAlpha': _xml_helpers.readIntItem,
 'hintText': _xml_helpers.readI18nStringItem,
 'toolTipText': _xml_helpers.readI18nStringItem,
 'numberOfMessagesInHistory': _xml_helpers.readIntItem,
 'alphaForLastMessages': _xml_helpers.readIntItem,
 'chatIsLockedToolTipText': _xml_helpers.readI18nStringItem,
 'recoveredLatestMessages': _xml_helpers.readI18nStringItem,
 'lifeTimeRecoveredMessages': _xml_helpers.readI18nStringItem}
_SETTINGS_LOADERS = {'lobby': (_readSettings, _LOBBY_SET_READERS, _LOBBY_ITEM_READERS),
 'battle': (_readSettings, _BATTLE_SET_READERS, _BATTLE_ITEM_READERS)}

def load(xmlCtx, section, messengerSettings):
    for tagName, subSec in section.items():
        if tagName != 'settings':
            raise _xml_helpers.XMLError(xmlCtx, 'Tag "{0:>s}" is invalid'.format(tagName))
        name = _xml_helpers.readNoEmptyStr(xmlCtx, subSec, 'name', 'Setting name is not defined')
        if name not in _SETTINGS_LOADERS:
            raise _xml_helpers.XMLError(xmlCtx, 'Setting "{0:>s}" is not valid'.format(name))
        loader, setReaders, itemReaders = _SETTINGS_LOADERS[name]
        if hasattr(messengerSettings, name):
            loader(xmlCtx.next(subSec), subSec, getattr(messengerSettings, name), setReaders, itemReaders)
        else:
            raise _xml_helpers.XMLError(xmlCtx, 'Settings has not attribute {0:>s}'.format(name))
