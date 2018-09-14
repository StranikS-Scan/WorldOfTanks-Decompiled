# Embedded file name: scripts/client/gui/doc_loaders/messages_panel_reader.py
from collections import namedtuple
from helpers import html
import resource_helper
_MessagesSettings = namedtuple('_MessagesSettings', ('maxLinesCount', 'direction', 'lifeTime', 'alphaSpeed', 'showUniqueOnly'))

def _getDefaultSettings():
    return {'maxLinesCount': -1,
     'direction': 'up',
     'lifeTime': 0.0,
     'alphaSpeed': 0.0,
     'showUniqueOnly': False}


def _readSettings(ctx, root):
    ctx, section = resource_helper.getSubSection(ctx, root, 'settings')
    settings = _getDefaultSettings()
    for ctx, subSection in resource_helper.getIterator(ctx, section):
        item = resource_helper.readItem(ctx, subSection, 'setting')
        settings[item.name] = item.value

    return _MessagesSettings(**settings)


def _readMessages(ctx, root):
    ctx, section = resource_helper.getSubSection(ctx, root, 'messages')
    messages = {}
    for ctx, subSection in resource_helper.getIterator(ctx, section):
        item = resource_helper.readItem(ctx, subSection, 'message')
        text, aliases = item.value
        aliases = aliases.split(',', 1)
        if len(aliases) == 1:
            aliases *= 2
        messages[item.name] = (html.translation(text), tuple(aliases))

    return messages


def _readXML(path):
    with resource_helper.root_generator(path) as ctx, root:
        settings = _readSettings(ctx, root)
        messages = _readMessages(ctx, root)
    return (settings, messages)


def _initCache(*paths):
    cache = {}
    for path in paths:
        cache[path] = _readXML(path)

    return cache


_cache = _initCache('gui/player_messages_panel.xml', 'gui/vehicle_errors_panel.xml', 'gui/vehicle_messages_panel.xml')

def readXML(path):
    global _cache
    if path in _cache:
        return _cache[path]
    result = _readXML(path)
    _cache[path] = result
    return result
