# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/battle_modifiers.py
from extension_utils import ResMgr
from battle_modifiers_common import battle_modifiers
from battle_modifiers_common.battle_modifiers import BattleParams
from battle_modifiers_ext import battle_params
from battle_modifiers_ext.battle_params import BattleParam, FakeBattleParam
from battle_modifiers_ext.battle_modifier.modifier_filters import ModificationTree
from battle_modifiers_ext.constants_ext import BATTLE_MODIFIERS_DIR, BATTLE_MODIFIERS_XML, ERROR_TEMPLATE, FAKE_MODIFIER_NAME, FAKE_PARAM_NAME, UseType, GameplayImpact, ModifierRestriction, NodeType
from typing import TYPE_CHECKING, Optional, Any, Tuple, Union, List
from soft_exception import SoftException
from debug_utils import LOG_WARNING, LOG_DEBUG
from constants import IS_DEVELOPMENT, IS_BASEAPP
from ResMgr import DataSection
from collections import OrderedDict
if TYPE_CHECKING:
    from battle_modifiers_common import ModifiersContext
g_cache = None

class ModifierBase(object):
    __slots__ = ('param', 'useType', 'value', 'gameplayImpact', 'minValue', 'maxValue', '_descr', '_id')

    def __init__(self, source):
        self.param = None
        self.useType = UseType.UNDEFINED
        self.value = 0.0
        self.minValue = None
        self.maxValue = None
        self._descr = None
        self._id = None
        if isinstance(source, DataSection):
            self._readConfig(source)
        else:
            self._initFromDescr(source)
        return

    def isFake(self):
        raise NotImplementedError

    def descr(self):
        if self._descr is None:
            self._descr = self._makeDescr()
        return self._descr

    def id(self):
        if self._id is None:
            self._id = self._makeId()
        return self._id

    def _initFromDescr(self, descr):
        raise NotImplementedError

    def _readConfig(self, config):
        self.param = self._readParam(config)
        self.gameplayImpact = self.__readGameplayImpact(config)

    def _readParam(self, config):
        raise NotImplementedError

    def _makeDescr(self):
        raise NotImplementedError

    def _makeId(self):
        raise NotImplementedError

    def __readGameplayImpact(self, config):
        if not config.has_key('gameplayImpact'):
            return GameplayImpact.UNDEFINED
        gameplayImpactName = config['gameplayImpact'].asString
        if gameplayImpactName not in GameplayImpact.NAMES:
            raise SoftException("[BattleModifiers] Unknown gameplay impact '{}'".format(gameplayImpactName))
        return GameplayImpact.NAME_TO_ID[gameplayImpactName]


class BattleModifier(ModifierBase):
    __slots__ = ('__modificationTree',)

    def __init__(self, source):
        self.__modificationTree = None
        super(BattleModifier, self).__init__(source)
        rootNode = self.__modificationTree.nodes.get(NodeType.ROOT)
        if rootNode:
            self.useType = rootNode.useType
            self.value = rootNode.value
            self.minValue = rootNode.minValue
            self.maxValue = rootNode.maxValue
        return

    def __call__(self, value, ctx=None):
        return self.__modificationTree(value, ctx)

    def __hash__(self):
        return self.id()

    def __eq__(self, other):
        return self.id() == other.id()

    def __repr__(self):
        return 'BattleModifier(paramName = {}, gameplayImpactName = {}, modificationTree = {})'.format(self.param.name, GameplayImpact.ID_TO_NAME[self.gameplayImpact], self.__modificationTree)

    def isFake(self):
        return False

    def _initFromDescr(self, descr):
        packed, treeDescr = descr
        self.param = battle_params.g_cache[packed >> 3]
        self.gameplayImpact = packed >> 1 & 3
        self.__modificationTree = ModificationTree(treeDescr, self.param)
        self._descr = descr

    def _readConfig(self, config):
        super(BattleModifier, self)._readConfig(config)
        self.__modificationTree = ModificationTree(config, self.param)

    def _readParam(self, config):
        paramName = config.name
        paramId = battle_params.g_cache.nameToId(paramName)
        if paramId is None:
            raise SoftException("[BattleModifiers] Unknown param name '{}'".format(paramName))
        return battle_params.g_cache[paramId]

    def _makeDescr(self):
        packed = self.param.id << 3 | self.gameplayImpact << 1 | self.isFake()
        return (packed, self.__modificationTree.descr())

    def _makeId(self):
        return hash((self.param.id, self.__modificationTree.id()))


class FakeBattleModifier(ModifierBase):
    __slots__ = ()

    def __repr__(self):
        return 'FakeBattleModifier(descr = {})'.format(self.descr())

    def isFake(self):
        return True

    def _initFromDescr(self, descr):
        limitsIdx = 3
        packed, value, paramDescr = descr[:limitsIdx]
        self.param = FakeBattleParam(paramDescr)
        self.useType = packed >> 5 & 3
        self.gameplayImpact = packed >> 3 & 3
        self.value = value
        if packed & 4:
            self.minValue = descr[limitsIdx]
            limitsIdx += 1
        if packed & 2:
            self.maxValue = descr[limitsIdx]
        self._descr = descr

    def _readConfig(self, config):
        super(FakeBattleModifier, self)._readConfig(config)
        self.value = self.__readValue(config)
        self.useType = self.__readUseType(config)
        self.minValue, self.maxValue = self.__readRestrictions(config)

    def _readParam(self, config):
        if not config.has_key(FAKE_PARAM_NAME):
            raise SoftException('Missing fakeParams section in FakeBattleModifier')
        return FakeBattleParam(config[FAKE_PARAM_NAME])

    def _makeDescr(self):
        packed = self.useType << 5 | self.gameplayImpact << 3 | self.isFake()
        descr = [packed, self.value, self.param.descr()]
        if self.minValue is not None:
            descr[0] |= 4
            descr.append(self.minValue)
        if self.maxValue is not None:
            descr[0] |= 2
            descr.append(self.maxValue)
        return tuple(descr)

    def _makeId(self):
        pass

    def __readValue(self, config):
        return 0.0 if not config.has_key('value') else config['value'].asFloat

    def __readUseType(self, config):
        useType = UseType.UNDEFINED
        if config.has_key('useType'):
            useTypeName = config['useType'].asString
            if useTypeName not in UseType.NAMES:
                raise SoftException("[BattleModifiers] Unknown use type '{}'".format(useTypeName))
            useType = UseType.NAME_TO_ID[useTypeName]
        clientData = self.param.clientData
        if useType not in clientData.useTypes:
            raise SoftException(ERROR_TEMPLATE.format('[Fake modifier] You should define physical type to unlock dimensional use types', clientData.resName))
        return useType

    def __readRestrictions(self, config):
        minValue = None
        maxValue = None
        if not config.has_key('restrictions'):
            return (minValue, maxValue)
        else:
            restrictionSection = config['restrictions']
            minLabel = ModifierRestriction.ID_TO_NAME[ModifierRestriction.MIN]
            maxLabel = ModifierRestriction.ID_TO_NAME[ModifierRestriction.MAX]
            if restrictionSection.has_key(minLabel):
                minValue = restrictionSection[minLabel].asFloat
            if restrictionSection.has_key(maxLabel):
                maxValue = restrictionSection[maxLabel].asFloat
            return (minValue, maxValue)


class BattleModifiers(battle_modifiers.BattleModifiers):
    __slots__ = ('__modifiers', '__domain', '__id', '__descr', '__battleDescr')

    def __init__(self, source=None):
        super(BattleModifiers, self).__init__(source)
        self.__modifiers = OrderedDict()
        self.__domain = 0
        self.__id = None
        self.__descr = None
        self.__battleDescr = None
        if source is not None:
            if isinstance(source, DataSection):
                self.__readConfig(source)
            else:
                self.__initFromDescr(source)
        return

    def __call__(self, paramId, value, ctx=None):
        return self.__modifiers[paramId](value, ctx) if paramId in self.__modifiers else value

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

    @staticmethod
    def retrieveBattleDescr(descr):
        res = []
        for modifierDescr in descr:
            if not _isFakeDescr(modifierDescr):
                res.append(modifierDescr)

        return tuple(res)

    def get(self, paramId):
        return self.__modifiers.get(paramId)

    def descr(self):
        if self.__descr is None:
            self.__descr = tuple((modifier.descr() for modifier in self.__modifiers.itervalues()))
        return self.__descr

    def battleDescr(self):
        if self.__battleDescr is None:
            self.__battleDescr = tuple((modifier.descr() for modifier in self.__modifiers.itervalues() if not modifier.isFake()))
        return self.__battleDescr

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
        fakeId = BattleParams.MAX + 1
        for modifierName, modifierSection in config.items():
            if modifierName == 'xmlns:xmlref':
                continue
            if modifierName == FAKE_MODIFIER_NAME:
                modifier = FakeBattleModifier(modifierSection)
                modifiers[fakeId] = modifier
                fakeId = fakeId + 1
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
        fakeId = BattleParams.MAX + 1
        for modifierDescr in descr:
            if _isFakeDescr(modifierDescr):
                modifier = FakeBattleModifier(modifierDescr)
                modifiers[fakeId] = modifier
                fakeId = fakeId + 1
                continue
            modifier = BattleModifier(modifierDescr)
            modifiers[modifier.param.id] = modifier
            domain |= modifier.param.domain

        self.__domain = domain

    def __makeId(self):
        ids = [ modifier.id() for modifier in self.__modifiers.itervalues() if not modifier.isFake() ]
        ids.sort()
        return hash(tuple(ids))


def getGlobalModifiers():
    global g_cache
    if g_cache is None:
        g_cache = _readGlobalBattleModifiers()
    return g_cache


def _readGlobalBattleModifiers():
    if not IS_DEVELOPMENT or not IS_BASEAPP:
        return BattleModifiers()
    modifiersSection = _readModifiersSection()
    if not modifiersSection:
        return BattleModifiers()
    modifiers = BattleModifiers(modifiersSection)
    LOG_DEBUG('[BattleModifiers] Use global battle modifiers: {}'.format(modifiers))
    return modifiers


def _readModifiersSection():
    config = ResMgr.openSection(BATTLE_MODIFIERS_DIR + BATTLE_MODIFIERS_XML)
    if config is None:
        return
    else:
        return ResMgr.openSection(BATTLE_MODIFIERS_DIR + config['config'].asString) if config.has_key('config') and config['config'].asString else config['modifiers']


def _isFakeDescr(descr):
    return descr[0] & 1
