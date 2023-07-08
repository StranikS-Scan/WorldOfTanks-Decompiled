# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/helpers/server_settings.py
from collections import namedtuple
from fun_random_common.fun_constants import DEFAULT_ASSETS_PACK, DEFAULT_SETTINGS_KEY, DEFAULT_PRIORITY, UNKNOWN_WWISE_REMAPPING, UNKNOWN_EVENT_ID, FunSubModeImpl
from shared_utils import makeTupleByDict

class FunSubModeClientConfig(namedtuple('_FunSubModeClientConfig', ('subModeImpl', 'assetsPointer', 'settingsKey', 'priority', 'wwiseRemapping', 'battleModifiersDescr', 'infoPageUrl'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(subModeImpl=FunSubModeImpl.DEFAULT, assetsPointer=DEFAULT_ASSETS_PACK, settingsKey=DEFAULT_SETTINGS_KEY, priority=DEFAULT_PRIORITY, wwiseRemapping=UNKNOWN_WWISE_REMAPPING, battleModifiersDescr=(), infoPageUrl='')
        defaults.update(kwargs)
        return super(FunSubModeClientConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls(FunSubModeImpl.DEFAULT, DEFAULT_ASSETS_PACK, DEFAULT_SETTINGS_KEY, DEFAULT_PRIORITY, UNKNOWN_WWISE_REMAPPING, (), '')


class FunSubModeFiltrationConfig(namedtuple('FunSubModeFiltrationConfig', ('levels', 'forbiddenClassTags', 'forbiddenVehTypes', 'allowedVehTypes'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(levels=(), forbiddenClassTags=set(), forbiddenVehTypes=set(), allowedVehTypes=set())
        defaults.update(kwargs)
        return super(FunSubModeFiltrationConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls((), set(), set(), set())


class FunSubModeSeasonalityConfig(namedtuple('FunSubModeSeasonalityConfig', ('isEnabled', 'peripheryIDs', 'seasons', 'primeTimes', 'cycleTimes'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, peripheryIDs=set(), seasons={}, primeTimes={}, cycleTimes=())
        defaults.update(kwargs)
        cls.__packSeasonalityConfig(defaults)
        return super(FunSubModeSeasonalityConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls(False, set(), {}, {}, ())

    def asDict(self):
        return self._asdict()

    @classmethod
    def __packSeasonalityConfig(cls, data):
        data['primeTimes'] = {int(peripheryID):value for peripheryID, value in data['primeTimes'].iteritems()}
        data['seasons'] = {int(seasonID):value for seasonID, value in data['seasons'].iteritems()}


class FunSubModeConfig(namedtuple('_FunSubModeConfig', ('eventID', 'isEnabled', 'seasonality', 'filtration', 'client'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(eventID=UNKNOWN_EVENT_ID, isEnabled=False, seasonality={}, filtration={}, client={})
        allowedFields = defaults.keys()
        defaults.update(kwargs)
        cls.__packConfigPart(FunSubModeClientConfig, 'client', defaults)
        cls.__packConfigPart(FunSubModeFiltrationConfig, 'filtration', defaults)
        cls.__packConfigPart(FunSubModeSeasonalityConfig, 'seasonality', defaults)
        defaults = cls.__filterAllowedFields(defaults, allowedFields)
        return super(FunSubModeConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls(UNKNOWN_EVENT_ID, False, {}, {}, {})

    @classmethod
    def __filterAllowedFields(cls, data, allowedFields):
        return dict(((k, v) for k, v in data.iteritems() if k in allowedFields))

    @classmethod
    def __packConfigPart(cls, configPartCls, configPartName, data):
        data[configPartName] = makeTupleByDict(configPartCls, data)


class FunProgressionConfig(namedtuple('_FunProgressionConfig', ('name', 'executors', 'conditions'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(name='', executors=(), conditions=())
        defaults.update(kwargs)
        return super(FunProgressionConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls('', (), ())


class FunMetaProgressionConfig(namedtuple('_FunMetaProgressionConfig', ('isEnabled', 'progressions'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, progressions=())
        defaults.update(kwargs)
        cls.__packProgressionsConfigs(defaults)
        return super(FunMetaProgressionConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls(False, ())

    @classmethod
    def __packProgressionsConfigs(cls, data):
        data['progressions'] = tuple((makeTupleByDict(FunProgressionConfig, p) for p in data['progressions']))


class FunRandomConfig(namedtuple('_FunRandomConfig', ('isEnabled', 'subModes', 'metaProgression', 'assetsPointer', 'settingsKey', 'infoPageUrl'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, subModes={}, metaProgression={}, assetsPointer=DEFAULT_ASSETS_PACK, settingsKey=DEFAULT_SETTINGS_KEY, infoPageUrl='')
        allowedFields = defaults.keys()
        defaults.update(kwargs)
        cls.__packSubModesConfigs(defaults)
        cls.__packMetaProgressionConfig(defaults)
        defaults = cls.__filterAllowedFields(defaults, allowedFields)
        return super(FunRandomConfig, cls).__new__(cls, **defaults)

    @classmethod
    def defaults(cls):
        return cls(False, {}, {}, DEFAULT_ASSETS_PACK, DEFAULT_SETTINGS_KEY, '')

    def replace(self, data):
        data = self.__packSubModesConfigs(data)
        data = self.__packMetaProgressionConfig(data)
        dataToUpdate = self.__filterAllowedFields(data, self._fields)
        return self._replace(**dataToUpdate)

    @classmethod
    def __filterAllowedFields(cls, data, allowedFields):
        return dict(((k, v) for k, v in data.iteritems() if k in allowedFields))

    @classmethod
    def __packMetaProgressionConfig(cls, data):
        progression = data['metaProgression'] if data['isEnabled'] else {}
        data['metaProgression'] = makeTupleByDict(FunMetaProgressionConfig, progression)
        return data

    @classmethod
    def __packSubModesConfigs(cls, data):
        events = data['events'] if data['isEnabled'] else {}
        data['subModes'] = {int(eID):FunSubModeConfig(**eData) for eID, eData in events.iteritems() if eData.get('isEnabled', False) and eData.get('eventID', UNKNOWN_EVENT_ID)}
        return data
