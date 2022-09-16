# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/battle_params.py
from extension_utils import ResMgr
from constants import IS_CLIENT
from typing import TYPE_CHECKING, Optional, Tuple, List, Set, Type
from battle_modifier_constants import BATTLE_PARAMS_XML_PATH, DataType, UseType, PhysicalType, ModifierDomain, ClientDomain, ModifierRestriction
from battle_modifier_restrictions import g_modifierValidators, MinLimiter, MaxLimiter, MinMaxLimiter
from battle_modifier_readers import registerParamReaders
from battle_modifier_appliers import registerParamAppliers
from soft_exception import SoftException
if TYPE_CHECKING:
    from ResMgr import DataSection
    from battle_modifier_restrictions import IModifierValidator, IValueLimiter
    from battle_modifiers import BattleModifier
_ERR_TEMPLATE = "[BattleParams] {} for param '{}'"
g_cache = None

class ClientParamData(object):
    __slots__ = ('domain', 'physicalType', 'useTypes')

    def __init__(self, techName, clientConfig):
        self.domain = self.__readDomain(techName, clientConfig)
        self.physicalType = self.__readPhysicalType(techName, clientConfig)
        self.useTypes = self.__readUseTypes(techName, self.physicalType, clientConfig)

    def __repr__(self):
        return 'ClientParamData(domain = {}, physicalTypeName={}, useTypesName={})'.format(self.domain, PhysicalType.ID_TO_NAME[self.physicalType], (UseType.ID_TO_NAME[useType] for useType in self.useTypes))

    @staticmethod
    def __readDomain(tName, dataSection):
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

    @staticmethod
    def __readUseTypes(tName, physicalType, dataSection):
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


class BattleParam(object):
    __slots__ = ('id', 'name', 'dataType', 'domain', 'clientData', 'valueLimiter', '__validators')

    def __init__(self, config):
        self.__readConfig(config)

    def __repr__(self):
        return "BattleParam(id = {}, name = '{}', dataTypeName = {}, clientData={})".format(self.id, self.name, DataType.ID_TO_NAME[self.dataType], self.clientData)

    def validate(self, battleModifier):
        for validator in self.__validators:
            validator(battleModifier)

    def __readConfig(self, config):
        paramId = self.__readId(config)
        dataType = self.__readDataType(config)
        registerParamReaders(paramId, dataType)
        registerParamAppliers(paramId, dataType)
        self.name = config.name
        self.id = paramId
        self.dataType = dataType
        self.domain = self.__readDomain(config)
        self.clientData = self.__readClientData(config)
        self.__validators, self.valueLimiter = self.__readRestrictions(config, paramId)

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
            if not config.has_key('client'):
                raise SoftException(_ERR_TEMPLATE.format('Missing client section', config.name))
            return ClientParamData(config.name, config['client'])

    @staticmethod
    def __readRestrictions(config, paramId):
        if not config.has_key('restrictions'):
            return ([], None)
        else:
            validators = {}
            valueLimiter = None
            minValue = None
            maxValue = None
            for restrictionName, restrictionSection in config['restrictions'].items():
                if restrictionName not in ModifierRestriction.NAMES:
                    raise SoftException("[BattleParams] Unknown restriction '{}'".format(restrictionName))
                restrictionId = ModifierRestriction.NAME_TO_ID[restrictionName]
                if restrictionId in validators:
                    raise SoftException(_ERR_TEMPLATE.format("Duplicate restriction '{}'".format(restrictionName), config.name))
                validator = g_modifierValidators[restrictionId](restrictionSection, paramId)
                if restrictionId == ModifierRestriction.MIN:
                    minValue = validator.arg
                if restrictionId == ModifierRestriction.MAX:
                    maxValue = validator.arg
                validators[restrictionId] = validator

            if minValue is not None and maxValue is not None:
                if minValue > maxValue:
                    raise SoftException(_ERR_TEMPLATE.format('Incorrect limits', config.name))
                valueLimiter = MinMaxLimiter(minValue, maxValue)
            elif minValue is not None:
                valueLimiter = MinLimiter(minValue)
            elif maxValue is not None:
                valueLimiter = MaxLimiter(maxValue)
            return (validators.values(), valueLimiter)


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
