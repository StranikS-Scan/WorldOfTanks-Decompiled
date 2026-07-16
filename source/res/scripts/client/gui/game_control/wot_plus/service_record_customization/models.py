# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus/service_record_customization/models.py
from __future__ import absolute_import
import logging
import typing
import ResMgr
from dict2model import fields, schemas, validate
from dict2model.models import Model
from gui.impl.lobby.offers import getGfImagePath
from helpers import getClientLanguage
from web.cache.web_cache import generateKey
if typing.TYPE_CHECKING:
    from typing import Any, Dict, List, Optional
    from web.cache.web_cache import BaseExternalCache
_logger = logging.getLogger(__name__)

class RibbonUrls(Model):
    __slots__ = ('base', 'icon', 'small', 'large', '_urlHashes', '_fileCache')

    def __init__(self, base, icon, small, large):
        super(RibbonUrls, self).__init__()
        self.base = base
        self.icon = icon
        self.small = small
        self.large = large
        self._fileCache = None
        self._urlHashes = [generateKey(base),
         generateKey(icon),
         generateKey(small),
         generateKey(large)]
        return

    def getBaseAsset(self):
        return self._getGFPath(self.base)

    def getIconAsset(self):
        return self._getGFPath(self.icon)

    def getSmallAsset(self):
        return self._getGFPath(self.small)

    def getLargeAsset(self):
        return self._getGFPath(self.large)

    def isDownloaded(self):
        return all((_hash in self._fileCache.getLoaded() for _hash in self._urlHashes))

    def setFileCache(self, fileCache):
        self._fileCache = fileCache

    def _getGFPath(self, url):
        path = self._fileCache.get(url)
        return getGfImagePath(path)


class BackgroundModel(Model):
    __slots__ = ('id', 'url', 'name', 'localization', '_langCode', '_localizationText', '_urlHash', '_fileCache')

    def __init__(self, id, name, url, localization):
        super(BackgroundModel, self).__init__()
        self.id = id
        self.url = url
        self.localization = localization
        self.name = name
        self._langCode = getClientLanguage()
        self._localizationText = None
        self._urlHash = generateKey(url)
        return

    def isDownloaded(self):
        return self._urlHash in self._fileCache.getLoaded()

    def getAsset(self):
        path = self._fileCache.get(self.url)
        return getGfImagePath(path)

    def getLocalization(self):
        return self._localizationText if self._localizationText is not None else self._loadLocalizationText()

    def setFileCache(self, fileCache):
        self._fileCache = fileCache

    def _loadLocalizationText(self):
        try:
            localizationPath = self._fileCache.get(self.localization)
            localizationRes = ResMgr.openSection(localizationPath)
            titleSection = localizationRes['title']
            if titleSection:
                text = titleSection.readString(self._langCode, default=None)
                if text is None:
                    _logger.warning('Cannot find text for background with id %s for lang code %s', self.id, self._langCode)
                self._localizationText = text or ''
        except IOError:
            _logger.exception('Failed to load localization text for background with id %s for lang code %s', self.id, self._langCode)

        return self._localizationText


class RibbonModel(Model):
    __slots__ = ('id', 'urls', 'name', '_urls')

    def __init__(self, id, name, urls):
        super(RibbonModel, self).__init__()
        self.id = id
        self.urls = urls
        self.name = name
        self._urls = [self.urls.base,
         self.urls.small,
         self.urls.large,
         self.urls.icon]

    @property
    def allURLs(self):
        return self._urls

    def isDownloaded(self):
        return self.urls.isDownloaded()

    def setFileCache(self, fileCache):
        self.urls.setFileCache(fileCache)


class RibbonUrlsLocal(RibbonUrls):
    __slots__ = ()

    def __init__(self, base, icon, small, large):
        super(RibbonUrlsLocal, self).__init__(base, icon, small, large)
        self._fileCache = None
        self._urlHashes = []
        return

    def getBaseAsset(self):
        return self.base

    def getIconAsset(self):
        return self.icon

    def getSmallAsset(self):
        return self.small

    def getLargeAsset(self):
        return self.large

    def isDownloaded(self):
        return True

    def setFileCache(self, fileCache):
        pass


class BackgroundModelLocal(BackgroundModel):
    __slots__ = ()

    def __init__(self, id, name, url, localization):
        super(BackgroundModelLocal, self).__init__(id, name, url, localization)
        self._localizationText = None
        self._urlHash = None
        return

    def getAsset(self):
        return self.url

    def getLocalization(self):
        return self.localization

    def isDownloaded(self):
        return True

    def setFileCache(self, fileCache):
        pass


class ConfigModel(Model):
    __slots__ = ('ribbons', 'backgrounds', '_ribbonURLs', '_backgroundIDsMap', '_ribbonsIDsMap', '_fileCache')

    def __init__(self, ribbons, backgrounds):
        super(ConfigModel, self).__init__()
        self.ribbons = sorted(ribbons, key=lambda ribbon: ribbon.id)
        self.backgrounds = sorted(backgrounds, key=lambda background: background.id)
        self._fileCache = None
        self._ribbonURLs = [ url for ribbon in ribbons for url in ribbon.allURLs ]
        self._backgroundIDsMap = {background.id:background for background in backgrounds}
        self._ribbonsIDsMap = {ribbon.id:ribbon for ribbon in ribbons}
        return

    @property
    def ribbonURLs(self):
        return self._ribbonURLs

    def getBackground(self, id_):
        return self._backgroundIDsMap.get(id_, None)

    def getRibbon(self, id_):
        return self._ribbonsIDsMap.get(id_, None)

    def setFileCache(self, fileCache):
        self._fileCache = fileCache
        self._setFileCacheForChildren(fileCache)

    def _setFileCacheForChildren(self, fileCache):
        for background in self.backgrounds:
            background.setFileCache(fileCache)

        for ribbon in self.ribbons:
            ribbon.setFileCache(fileCache)


backgroundSchema = schemas.Schema(fields={'id': fields.Integer(required=True),
 'name': fields.String(required=True),
 'url': fields.String(required=True, serializedValidators=validate.Length(minValue=1), deserializedValidators=validate.Length(minValue=1)),
 'localization': fields.String(required=True, serializedValidators=validate.Length(minValue=1), deserializedValidators=validate.Length(minValue=1))}, modelClass=BackgroundModel, checkUnknown=True)
ribbonUrlsSchema = schemas.Schema(fields={'base': fields.String(required=True, serializedValidators=validate.Length(minValue=1), deserializedValidators=validate.Length(minValue=1)),
 'icon': fields.String(required=True, serializedValidators=validate.Length(minValue=1), deserializedValidators=validate.Length(minValue=1)),
 'small': fields.String(required=True, serializedValidators=validate.Length(minValue=1), deserializedValidators=validate.Length(minValue=1)),
 'large': fields.String(required=True, serializedValidators=validate.Length(minValue=1), deserializedValidators=validate.Length(minValue=1))}, modelClass=RibbonUrls, checkUnknown=True)
ribbonSchema = schemas.Schema(fields={'id': fields.Integer(required=True),
 'name': fields.String(required=True),
 'urls': ribbonUrlsSchema}, modelClass=RibbonModel, checkUnknown=True)
configSchema = schemas.Schema(fields={'ribbons': fields.List(fieldOrSchema=ribbonSchema, required=True),
 'backgrounds': fields.List(fieldOrSchema=backgroundSchema, required=True)}, modelClass=ConfigModel, checkUnknown=True)
backgroundLocalSchema = schemas.Schema(fields={'id': fields.Integer(required=True),
 'name': fields.String(required=True),
 'url': fields.String(required=True),
 'localization': fields.String(required=True)}, modelClass=BackgroundModelLocal, checkUnknown=True)
ribbonUrlsLocalSchema = schemas.Schema(fields={'base': fields.String(required=True),
 'icon': fields.String(required=True),
 'small': fields.String(required=True),
 'large': fields.String(required=True)}, modelClass=RibbonUrlsLocal, checkUnknown=True)
ribbonLocalSchema = schemas.Schema(fields={'id': fields.Integer(required=True),
 'name': fields.String(required=True),
 'urls': ribbonUrlsLocalSchema}, modelClass=RibbonModel, checkUnknown=True)
localConfigSchema = schemas.Schema(fields={'ribbons': fields.List(fieldOrSchema=ribbonLocalSchema, required=True),
 'backgrounds': fields.List(fieldOrSchema=backgroundLocalSchema, required=True)}, modelClass=ConfigModel, checkUnknown=True)

def createConfigModel(rawData):
    return configSchema.deserialize(rawData, silent=True)


def createLocalConfigModel(rawData):
    return localConfigSchema.deserialize(rawData, silent=True)
