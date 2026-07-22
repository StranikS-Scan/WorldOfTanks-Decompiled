# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/battle_params.py
from battle_modifiers_common.battle_modifiers import BattleParams
from battle_modifiers_ext.battle_modifier.modifier_appliers import registerParamAppliers
from battle_modifiers_ext.battle_modifier.modifier_restrictions import readRestrictions
from battle_modifiers_ext.battle_modifier.modifier_readers import registerParamReaders
from battle_modifiers_ext.constants_ext import BATTLE_PARAMS_XML_PATH, FAKE_PARAM_NAME, DataType, UseType, PhysicalType, ModifierDomain, ClientDomain
from constants import IS_CLIENT
from extension_utils import ResMgr
from typing import Optional, Set, Tuple, Iterable, Union
from ResMgr import DataSection
from soft_exception import SoftException
_ERR_TEMPLATE = "[BattleParams] {} for param '{}'"
g_cache = None

class ClientParamData(object):
    __slots__ = ('resName', 'domain', 'physicalType', 'useTypes')

    def __init__(self, source, techName):
        if isinstance(source, DataSection):
            self._readConfig(techName, source)
        else:
            self._initFromDescr(source)

    def __repr__(self):
        return 'ClientParamData(resName={}, domain = {}, physicalTypeName={}, useTypesName={})'.format(self.resName, self.domain, PhysicalType.ID_TO_NAME[self.physicalType], (UseType.ID_TO_NAME[useType] for useType in self.useTypes))

    def descr(self):
        raise SoftException('ClientParamData can not be serialized')

    def _initFromDescr(self, descr):
        raise SoftException('ClientParamData can be constructed only from DataSection')

    def _readConfig(self, techName, clientConfig):
        self.resName = self._readResName(techName, clientConfig)
        self.physicalType = self.__readPhysicalType(techName, clientConfig)
        self.useTypes = self._readUseTypes(techName, self.physicalType, clientConfig)
        self.domain = self.__readDomain(techName, self.useTypes, clientConfig)

    @classmethod
    def _readResName(cls, techName, _):
        return techName

    @staticmethod
    def _readUseTypes(tName, physicalType, dataSection):
        useTypes = set()
        if not dataSection.has_key('useTypes'):
            return useTypes
        for useTypeName in dataSection['useTypes'].asString.split():
            if useTypeName not in UseType.NAMES:
                raise SoftException(_ERR_TEMPLATE.format("Unknown client use type '{}'".format(useTypeName), tName))
            useTypes.add(UseType.NAME_TO_ID[useTypeName])

        if physicalType == PhysicalType.UNDEFINED and useTypes & UseType.DIMENSIONAL_TYPES:
            raise SoftException(_ERR_TEMPLATE.format("Client physical type should be defined in order to show dimensional use types '{}'".format(', '.join((UseType.ID_TO_NAME[useType] for useType in UseType.DIMENSIONAL_TYPES))), tName))
        return useTypes

    @staticmethod
    def __readDomain(tName, useTypes, dataSection):
        clientDomain = ClientDomain.UNDEFINED
        if not useTypes:
            return clientDomain
        if not dataSection.has_key('domain'):
            raise SoftException(_ERR_TEMPLATE.format('Missing client domain', tName))
        clientDomain = dataSection['domain'].asString
        if clientDomain not in ClientDomain.ALL:
            raise SoftException(_ERR_TEMPLATE.format("Unknown client domain '{}'".format(clientDomain), tName))
        return clientDomain

    @staticmethod
    def __readPhysicalType(tName, dataSection):
        if not dataSection.has_key('physicalType'):
            return PhysicalType.UNDEFINED
        physTypeName = dataSection['physicalType'].asString
        if physTypeName not in PhysicalType.NAMES:
            raise SoftException(_ERR_TEMPLATE.format("Unknown client phys. type '{}'".format(physTypeName), tName))
        return PhysicalType.NAME_TO_ID[physTypeName]


class FakeClientParamData(ClientParamData):
    __slots__ = ('__descr',)

    def __init__(self, source, techName):
        super(FakeClientParamData, self).__init__(source, techName)
        self.__descr = None
        return

    def __repr__(self):
        return 'FakeClientParamData(descr = {})'.format(self.descr())

    def descr(self):
        if self.__descr is None:
            self.__descr = self.__makeDescr()
        return self.__descr

    @classmethod
    def _readResName(cls, techName, config):
        if not config.has_key('view'):
            raise SoftException('Missing view for a FakeBattleModifier')
        return config['view'].asString

    @classmethod
    def _readUseTypes(cls, tName, physicalType, dataSection):
        return cls.__getUseTypes(physicalType)

    def _initFromDescr(self, descr):
        self.resName, self.domain, self.physicalType = descr
        self.useTypes = self.__getUseTypes(self.physicalType)

    @classmethod
    def __getUseTypes(cls, physicalType):
        return UseType.NON_DIMENSIONAL_TYPES if physicalType == PhysicalType.UNDEFINED else UseType.ALL_WITH_UNDEFINED

    def __makeDescr(self):
        return (self.resName, self.domain, self.physicalType)


class BaseBattleParam(object):

    def __init__(self, source):
        if isinstance(source, DataSection):
            self._readConfig(source)
        else:
            self._initFromDescr(source)

    def descr(self):
        raise NotImplementedError

    def _initFromDescr(self, descr):
        raise NotImplementedError

    def _readConfig(self, config):
        raise NotImplementedError


class BattleParam(BaseBattleParam):
    __slots__ = ('id', 'name', 'clientData', 'dataType', 'domain', 'validators', 'minValue', 'maxValue')

    def __repr__(self):
        return "BattleParam(id = {}, name = '{}', dataTypeName = {}, clientData={})".format(self.id, self.name, DataType.ID_TO_NAME[self.dataType], self.clientData)

    def descr(self):
        raise SoftException('BattleParam can not be serialized')

    def _initFromDescr(self, descr):
        raise SoftException('BattleParam can only be constructed from DataSection')

    def _readConfig(self, config):
        paramId = self.__readId(config)
        dataType = self.__readDataType(config)
        registerParamReaders(paramId, dataType)
        registerParamAppliers(paramId, dataType)
        self.name = config.name
        self.id = paramId
        self.dataType = dataType
        self.domain = self.__readDomain(config)
        self.clientData = self.__readClientData(config)
        self.validators, self.minValue, self.maxValue = readRestrictions(config, self.id)

    @staticmethod
    def __readId(config):
        if not config.has_key('id'):
            raise SoftException(_ERR_TEMPLATE.format('Missing id', config.name))
        return config['id'].asInt

    @staticmethod
    def __readDataType(config):
        if not config.has_key('dataType'):
            raise SoftException(_ERR_TEMPLATE.format('Missing data type', config.name))
        dataTypeName = config['dataType'].asString
        if dataTypeName not in DataType.NAMES:
            raise SoftException(_ERR_TEMPLATE.format("Unknown data type '{}'".format(dataTypeName), config.name))
        return DataType.NAME_TO_ID[dataTypeName]

    @staticmethod
    def __readDomain(config):
        if not config.has_key('domain'):
            return ModifierDomain.DEFAULT
        domain = 0
        for domainName in config['domain'].asString.split():
            if domainName not in ModifierDomain.NAMES:
                raise SoftException(_ERR_TEMPLATE.format("Unknown domain '{}'".format(domainName), config.name))
            domain |= ModifierDomain.NAME_TO_ID[domainName]

        return domain

    @staticmethod
    def __readClientData(config):
        if not IS_CLIENT:
            return None
        else:
            clientSection = config['client'] if config.has_key('client') else config
            return ClientParamData(clientSection, config.name)


class FakeBattleParam(BaseBattleParam):
    __slots__ = ('id', 'name', 'clientData', '__descr')

    def __init__(self, source):
        super(FakeBattleParam, self).__init__(source)
        self.__descr = None
        return

    def __repr__(self):
        return 'FakeBattleParam(descr = {})'.format(self.descr())

    def descr(self):
        if self.__descr is None:
            self.__descr = self.__makeDescr()
        return self.__descr

    def _initFromDescr(self, descr):
        self.__initialize(descr)

    def _readConfig(self, config):
        self.__initialize(config)

    def __initialize(self, source):
        self.name = FAKE_PARAM_NAME
        self.id = BattleParams.FAKE_PARAM
        self.clientData = FakeClientParamData(source, self.name)

    def __makeDescr(self):
        return self.clientData.descr()


class BattleParamsCache(object):
    __slots__ = ('__params', '__nameToId')

    def __init__(self):
        self.__readConfig()

    def __iter__(self):
        return self.__params.iteritems()

    def __getitem__(self, id):
        return self.__params[id]

    def __len__(self):
        return len(self.__params)

    def __contains__(self, id):
        return id in self.__params

    def __repr__(self):
        return 'BattleParams({})'.format(self.__params.values())

    def get(self, id):
        return self.__params.get(id)

    def idToName(self, id):
        return self.__params[id].name

    def nameToId(self, name):
        return self.__nameToId.get(name)

    def __readConfig(self):
        config = ResMgr.openSection(BATTLE_PARAMS_XML_PATH)
        if config is None:
            raise SoftException("[BattleParams] Cannot open or read '{}'".format(BATTLE_PARAMS_XML_PATH))
        self.__params = params = {}
        self.__nameToId = nameToId = {}
        for paramName, paramSection in config.items():
            if paramName == 'xmlns:xmlref':
                continue
            param = BattleParam(paramSection)
            if param.id in params:
                raise SoftException('[BattleParams] Not unique id {}'.format(param.id))
            if param.name in nameToId:
                raise SoftException("[BattleParams] Not unique name '{}'".format(param.id))
            params[param.id] = param
            nameToId[param.name] = param.id

        return


def init():
    global g_cache
    g_cache = BattleParamsCache()
