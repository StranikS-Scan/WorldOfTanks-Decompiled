# Embedded file name: scripts/client/tutorial/doc_loader/gui_config.py
from collections import namedtuple
import resource_helper
__all__ = ('readConfig', 'clearConfig')
_cache = {}

def readConfig(path, forced = False):
    global _cache
    if not forced and path in _cache:
        return _cache[path]
    else:
        scenes, items, commands = (None, None, None)
        with resource_helper.root_generator(path) as ctx, root:
            scenes = _readConfig(ctx, root, 'scenes', 'scene', _SceneConfig)
            items = _readConfig(ctx, root, 'gui-items', 'item', _ItemConfig)
            commands = _readConfig(ctx, root, 'gui-commands', 'command', _CommandData)
        _cache[path] = _TutorialConfig(scenes, items, commands)
        return _cache[path]


def clearConfig(path):
    if path in _cache:
        del _cache[path]


_SceneConfig = namedtuple('_SceneConfig', ('sceneID', 'event'))
_ItemConfig = namedtuple('_ItemConfig', ('view', 'path', 'padding'))
_CommandData = namedtuple('_CommandData', ('type', 'name', 'args'))

class _TutorialConfig(object):
    __slots__ = ('__scenes', '__guiItems', '__commands')

    def __init__(self, scenes = None, items = None, commands = None):
        super(_TutorialConfig, self).__init__()
        self.__scenes = scenes or {}
        self.__guiItems = items or {}
        self.__commands = commands or {}

    def isEmpty(self):
        return not self.__scenes and not self.__guiItems and not self.__commands

    def getSceneID(self, guiPage):
        try:
            return self.__scenes[guiPage].sceneID
        except KeyError:
            return ''

    def getSceneEvent(self, sceneID):
        scenes = dict(map(lambda scene: (scene.sceneID, scene.event), self.__scenes.itervalues()))
        try:
            return scenes[sceneID]
        except KeyError:
            return ''

    def getItem(self, targetID):
        if targetID in self.__guiItems:
            return self.__guiItems[targetID]
        else:
            return None
            return None

    def getItems(self):
        for itemID, item in self.__guiItems.iteritems():
            yield (itemID, item)

    def getCommand(self, commandID):
        try:
            return self.__commands[commandID]
        except KeyError:
            return None

        return None

    def getCommands(self):
        for commandID, command in self.__commands.iteritems():
            yield (commandID, command)


_ITEM_TYPE = resource_helper.RESOURCE_ITEM_TYPE

def _readConfig(ctx, root, parentTag, childTag, itemClass):
    ctx, section = resource_helper.getSubSection(ctx, root, parentTag, safe=True)
    if not section:
        return {}
    config = {}
    for ctx, subSection in resource_helper.getIterator(ctx, section):
        item = resource_helper.readItem(ctx, subSection, childTag)
        if not item.type == _ITEM_TYPE.DICT:
            raise AssertionError('Type of value should be dict')
            name = item.name
            raise name in config and resource_helper.ResourceError(ctx, 'Item {0} is duplicated.'.format(name))
        config[name] = itemClass(**item.value)

    return config
