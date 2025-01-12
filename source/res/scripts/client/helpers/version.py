# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/version.py
import typing
import ResMgr
import section2dict
from dict2model import models, schemas, fields
from helpers import VERSION_FILE_PATH, LOC_VERSION_FILE_PATH
_clientVersion = None
_locVersion = None

class ClientVersionMetaModel(models.Model):
    __slots__ = ('client', 'overrides', 'realm', 'branch', 'buildScriptsRevision')

    def __init__(self, client='', overrides='', realm='', branch='', buildScriptsRevision=''):
        super(ClientVersionMetaModel, self).__init__()
        self.client = client
        self.overrides = overrides
        self.realm = realm
        self.branch = branch
        self.buildScriptsRevision = buildScriptsRevision

    def _reprArgs(self):
        return 'client={}, overrides={}, realm={}, branch={}, buildScriptsRevision={}'.format(self.client, self.overrides, self.realm, self.branch, self.buildScriptsRevision)


class ClientVersionModel(models.Model):
    __slots__ = ('appname', 'version', 'showLicense', 'ingameHelpVersion', 'meta')

    def __init__(self, appname='', version='', showLicense='', ingameHelpVersion='', meta=None):
        super(ClientVersionModel, self).__init__()
        self.appname = appname
        self.version = version
        self.showLicense = showLicense
        self.ingameHelpVersion = ingameHelpVersion
        self.meta = meta or ClientVersionMetaModel()

    def _reprArgs(self):
        return 'appname={}, version={}, showLicense={}, ingameHelpVersion={}, meta={}'.format(self.appname, self.version, self.showLicense, self.ingameHelpVersion, self.meta)


class LocalizationVersionModel(models.Model):
    __slots__ = ('version', 'revision', 'language')

    def __init__(self, version='', revision='', language=''):
        super(LocalizationVersionModel, self).__init__()
        self.version = version
        self.revision = revision
        self.language = language

    def _reprArgs(self):
        return 'version={}, revision={}, language={}'.format(self.version, self.revision, self.language)


_clientVersionMetaSchema = schemas.Schema[ClientVersionMetaModel](fields={'client': fields.String(required=False, default=''),
 'overrides': fields.String(required=False, default=''),
 'realm': fields.String(required=False, default=''),
 'branch': fields.String(required=False, default=''),
 'buildScriptsRevision': fields.String(required=False, default='')}, checkUnknown=False, modelClass=ClientVersionMetaModel)
_clientVersionSchema = schemas.Schema[ClientVersionModel](fields={'appname': fields.String(required=False, default=''),
 'version': fields.String(required=False, default=''),
 'showLicense': fields.String(required=False, default=''),
 'ingameHelpVersion': fields.String(required=False, default=''),
 'meta': fields.Nested(schema=_clientVersionMetaSchema, required=False, default=ClientVersionMetaModel)}, checkUnknown=False, modelClass=ClientVersionModel)
_localizationVersionSchema = schemas.Schema[LocalizationVersionModel](fields={'version': fields.String(required=False, default=''),
 'revision': fields.String(required=False, default=''),
 'language': fields.String(required=False, default='')}, checkUnknown=False, modelClass=LocalizationVersionModel)

def getClientVersion(force=False):
    global _clientVersion
    if _clientVersion is None or force:
        section = ResMgr.openSection(VERSION_FILE_PATH)
        _clientVersion = _clientVersionSchema.deserialize(section2dict.parse(section, normalizeValues=False) if section else {})
    return _clientVersion


def getLocalizationVersion(force=False):
    global _locVersion
    if _locVersion is None or force:
        section = ResMgr.openSection(LOC_VERSION_FILE_PATH)
        _locVersion = _localizationVersionSchema.deserialize(section2dict.parse(section, normalizeValues=False) if section else {})
    return _locVersion
