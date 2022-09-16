# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/battle_modifiers.py
import battle_params
import battle_modifier_readers
import battle_modifier_appliers
from extension_utils import ResMgr
from battle_modifiers_common import battle_modifiers
from battle_modifier_constants import UseType, GameplayImpact, BATTLE_MODIFIERS_DIR, BATTLE_MODIFIERS_XML
from typing import Optional, Any, Tuple, Union
from soft_exception import SoftException
from debug_utils import LOG_WARNING, LOG_DEBUG
from constants import IS_DEVELOPMENT, IS_BASEAPP
from ResMgr import DataSection
from collections import OrderedDict
g_cache = None
_ERROR_TEMPLATE = "[BattleModifiers] {} for param '{}'"

class BattleModifier(object):
    __slots__ = ('param', 'useType', 'value', 'gameplayImpact', '__id', '__descr', '__shouldLimit')

    def __init__(self, source):
        self.__id = None
        self.__descr = None
        if isinstance(source, DataSection):
            self.__readConfig(source)
            self.param.validate(self)
        else:
            self.__initFromDescr(source)
        self.__shouldLimit = self.useType != UseType.VAL and self.param.valueLimiter
        return

    def __call__(self, value):
        modifiedValue = battle_modifier_appliers.g_cache[self.param.id][self.useType](value, self.value)
        return self.param.valueLimiter(modifiedValue) if self.__shouldLimit else modifiedValue

    def __hash__(self):
        return self.id()

    def __eq__(self, other):
        return self.id() == other.id()

    def __repr__(self):
        return 'BattleModifier(paramName = {}, value = {}, useTypeName = {}, gameplayImpactName={})'.format(self.param.name, self.value, UseType.ID_TO_NAME[self.useType], GameplayImpact.ID_TO_NAME[self.gameplayImpact])

    def descr(self):
        if self.__descr is None:
            self.__descr = self.__makeDescr()
        return self.__descr

    def id(self):
        if self.__id is None:
            self.__id = self.__makeId()
        return self.__id

    @staticmethod
    def __readParam(config):
        paramName = config.name
        paramId = battle_params.g_cache.nameToId(paramName)
        if paramId is None:
            raise SoftException("[BattleModifiers] Unknown param name '{}'".format(paramName))
        return battle_params.g_cache[paramId]

    @staticmethod
    def __readUseType(config):
        if not config.has_key('useType'):
            raise SoftException(_ERROR_TEMPLATE.format('Missing use type', config.name))
        useTypeName = config['useType'].asString
        if useTypeName not in UseType.NAMES:
            raise SoftException("[BattleModifiers] Unknown use type '{}'".format(useTypeName))
        return UseType.NAME_TO_ID[useTypeName]

    @staticmethod
    def __readValue(config, param, useType):
        if not config.has_key('value'):
            raise SoftException(_ERROR_TEMPLATE.format('Missing value', config.name))
        return battle_modifier_readers.g_cache[param.id][useType](config['value'])

    @staticmethod
    def __readGameplayImpact(config):
        if not config.has_key('gameplayImpact'):
            return GameplayImpact.UNDEFINED
        gameplayImpactName = config['gameplayImpact'].asString
        if gameplayImpactName not in GameplayImpact.NAMES:
            raise SoftException("[BattleModifiers] Unknown gameplay impact '{}'".format(gameplayImpactName))
        return GameplayImpact.NAME_TO_ID[gameplayImpactName]

    def __readConfig(self, config):
        self.param = self.__readParam(config)
        self.useType = self.__readUseType(config)
        self.value = self.__readValue(config, self.param, self.useType)
        self.gameplayImpact = self.__readGameplayImpact(config)

    def __makeDescr(self):
        packed = self.param.id << 4 | self.useType << 2 | self.gameplayImpact
        return (packed, self.value)

    def __initFromDescr(self, descr):
        packed, value = descr
        self.param = battle_params.g_cache[packed >> 4]
        self.useType = packed >> 2 & 3
        self.gameplayImpact = packed & 3
        self.value = value

    def __makeId(self):
        return hash((self.param.id, self.useType, self.value))


class BattleModifiers(battle_modifiers.BattleModifiers):
    __slots__ = ('__modifiers', '__domain', '__id', '__descr')

    def __init__(self, source=None):
        super(BattleModifiers, self).__init__(source)
        self.__modifiers = OrderedDict()
        self.__domain = 0
        self.__id = None
        self.__descr = None
        if source is not None:
            if isinstance(source, DataSection):
                self.__readConfig(source)
            else:
                self.__initFromDescr(source)
        return

    def __call__(self, paramId, value):
        return self.__modifiers[paramId](value) if paramId in self.__modifiers else value

    def __iter__(self):
        return self.__modifiers.iteritems()

    def __getitem__(self, paramId):
        return self.__modifiers[paramId]

    def __len__(self):
        return len(self.__modifiers.items())

    def __contains__(self, paramId):
        return paramId in self.__modifiers

    def __nonzero__(self):
        return self.__domain

    def __hash__(self):
        return self.id()

    def __eq__(self, other):
        return self.id() == other.id()

    def __repr__(self):
        return 'BattleModifiers({})'.format(self.__modifiers.values())

    def get(self, paramId):
        return self.__modifiers.get(paramId)

    def descr(self):
        if self.__descr is None:
            self.__descr = tuple((modifier.descr() for modifier in self.__modifiers.itervalues()))
        return self.__descr

    def domain(self):
        return self.__domain

    def haveDomain(self, domain):
        return bool(self.__domain & domain)

    def id(self):
        if self.__id is None:
            self.__id = self.__makeId()
        return self.__id

    def __readConfig(self, config):
        modifiers = self.__modifiers
        domain = 0
        for modifierName, modifierSection in config.items():
            if modifierName == 'xmlns:xmlref':
                continue
            modifier = BattleModifier(modifierSection)
            if modifier.param.id in modifiers:
                paramName = modifier.param.name
                LOG_WARNING("[BattleModifiers] Ignore multiple modifiers for param '{}'".format(paramName))
                continue
            modifiers[modifier.param.id] = modifier
            domain |= modifier.param.domain

        self.__domain = domain

    def __initFromDescr(self, descr):
        modifiers = self.__modifiers
        domain = 0
        for modifierDescr in descr:
            modifier = BattleModifier(modifierDescr)
            modifiers[modifier.param.id] = modifier
            domain |= modifier.param.domain

        self.__domain = domain

    def __makeId(self):
        ids = [ modifier.id() for modifier in self.__modifiers.itervalues() ]
        ids.sort()
        return hash(tuple(ids))


def init():
    initGlobalBattleModifiers()


def initGlobalBattleModifiers():
    global g_cache
    if not IS_DEVELOPMENT or not IS_BASEAPP:
        return
    modifiersSection = _readModifiersSection()
    if modifiersSection:
        g_cache = BattleModifiers(modifiersSection)
        LOG_DEBUG('[BattleModifiers] Use global battle modifiers: {}'.format(g_cache))


def _readModifiersSection():
    config = ResMgr.openSection(BATTLE_MODIFIERS_DIR + BATTLE_MODIFIERS_XML)
    if config is None:
        return
    else:
        return ResMgr.openSection(BATTLE_MODIFIERS_DIR + config['config'].asString) if config.has_key('config') and config['config'].asString else config['modifiers']
