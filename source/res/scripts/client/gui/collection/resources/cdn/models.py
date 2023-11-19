# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/collection/resources/cdn/models.py
import typing
from enum import Enum, unique
from dict2model.models import Model
from gui.impl.utils.path import normalizeGfImagePath
from web.cache.web_cache import generateKey
if typing.TYPE_CHECKING:
    from typing import List
    from gui.collection.resources.cdn.cache import CollectionsCdnCache

@unique
class Group(str, Enum):
    ITEM = 'items'
    BG = 'backgrounds'


@unique
class Sub(str, Enum):
    ICON = '48x48'
    SMALLEST = '232x174'
    SMALL = '296x222'
    MEDIUM = '400x300'
    LARGE = '600x450'
    LARGEST = '1000x680'
    RECEIVED = 'received'
    UNRECEIVED = 'unreceived'
    BP_10 = 'battle_pass_10'
    BP_11 = 'battle_pass_11'
    BP_12 = 'battle_pass_12'


class ImageModel(Model):
    __slots__ = ('group', 'sub', 'name', 'url', '__id', '__imageCacheKey')

    def __init__(self, group, sub, name, url=None):
        super(ImageModel, self).__init__()
        self.group = group
        self.sub = sub
        self.name = name
        self.url = url
        self.__id = makeImageID(group, sub, name)
        self.__imageCacheKey = generateKey(self.url)

    @property
    def id(self):
        return self.__id

    def isDownloaded(self, fileCache):
        return self.__imageCacheKey in fileCache.getLoaded()

    def getGFPath(self, fileCache):
        return normalizeGfImagePath(fileCache.getRelativePath(self.url))

    def __repr__(self):
        return '<ImageModel(group={}, sub={}, name={})>'.format(self.group, self.sub, self.name)


class ConfigModel(Model):
    __slots__ = ('images',)

    def __init__(self, images):
        super(ConfigModel, self).__init__()
        self.images = images

    def __repr__(self):
        return '<ConfigModel(images={})>'.format(len(self.images))


class CdnCacheParamsModel(object):
    __slots__ = ('configUrl',)

    def __init__(self, configUrl=None):
        self.configUrl = configUrl

    @property
    def isReady(self):
        return bool(self.configUrl)

    def reset(self):
        self.configUrl = None
        return

    def __repr__(self):
        return '<CdnCacheParamsModel(configUrl={})>'.format(self.configUrl)


def makeImageID(group, sub, name):
    return '/'.join((Group(group), Sub(sub), name))
