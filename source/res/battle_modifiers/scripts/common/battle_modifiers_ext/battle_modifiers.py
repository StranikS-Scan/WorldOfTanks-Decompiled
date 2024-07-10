# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/battle_modifiers.py
from extension_utils import ResMgr
from battle_modifiers_common import battle_modifiers
from battle_modifiers_common.battle_modifiers import BattleParams, ModifierScope
from battle_modifiers_ext import battle_params
from battle_modifiers_ext.battle_params import BaseBattleParam, BattleParam, FakeBattleParam
from battle_modifiers_ext.battle_modifier import modifier_readers, modifier_appliers
from battle_modifiers_ext.battle_modifier.modifier_filters import ModificationTree
from battle_modifiers_ext.battle_modifier.modifier_helpers import Serializable
from battle_modifiers_ext.constants_ext import BATTLE_MODIFIERS_DIR, BATTLE_MODIFIERS_XML, ERROR_TEMPLATE, FAKE_PARAM_NAME, UseType, GameplayImpact, ModifierDomain, ModifierRestriction, NodeType
from battle_modifiers_ext.modification_cache import vehicle_modifications, constants_modifications
from typing import TYPE_CHECKING, Optional, Any, Tuple, Union, List
from soft_exception import SoftException
from debug_utils import LOG_WARNING, LOG_DEBUG
from constants import IS_DEVELOPMENT, IS_BASEAPP, IS_CLIENT
from ResMgr import DataSection
from collections import OrderedDict
if TYPE_CHECKING:
    from battle_modifiers_common import ModifiersContext
    from items.vehicles import VehicleType
    from battle_modifiers_common.battle_modifiers import ConstantsSet
    from battle_modifiers_ext.modification_cache.constants_modifications import ConstantsModification
g_cache = None

class ModifierBase(Serializable):
    __slots__ = ('param', 'useType', 'value', 'gameplayImpact', 'minValue', 'maxValue', '_descr', '_id')

    def __init__(self, source):
        self.param = None
        self.useType = UseType.UNDEFINED
        self.value = 0.0
        self.minValue = None
        self.maxValue = None
        self._descr = None
        self._id = None
        super(ModifierBase, self).__init__(source)
        return

    def hasUniqueID(self):
        return False

    def descr(self):
        if self._descr is None:
            self._descr = self._makeDescr()
        return self._descr

    def id(self):
        if self._id is None:
            self._id = self._makeId()
        return self._id

    def _initFromConfig(self, config, *args):
        self.param = self._configureParam(config)
        self.gameplayImpact = self._configureGameplayImpact(config)

    def _configureGameplayImpact(self, config):
        if not config.has_key('gameplayImpact'):
            return GameplayImpact.UNDEFINED
        gameplayImpactName = config['gameplayImpact'].asString
        if gameplayImpactName not in GameplayImpact.NAMES:
            raise SoftException("[BattleModifiers] Unknown gameplay impact '{}'".format(gameplayImpactName))
        return GameplayImpact.NAME_TO_ID[gameplayImpactName]

    def _configureParam(self, config):
        raise NotImplementedError

    def _makeDescr(self):
        raise NotImplementedError

    def _makeId(self):
        raise NotImplementedError


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

    def __repr__(self):
        return 'BattleModifier(paramId = {}, gameplayImpactName = {}, modificationTree = {})'.format(self.param.id, GameplayImpact.ID_TO_NAME[self.gameplayImpact], self.__modificationTree)

    def hasUniqueID(self):
        return self.param.isHashable()

    def _initFromDescr(self, descr):
        paramId, gameplayImpact, treeDescr = descr
        self.param = battle_params.g_cache[paramId]
        self.gameplayImpact = gameplayImpact
        self.__modificationTree = ModificationTree(treeDescr, self.param)
        self._descr = descr

    def _initFromConfig(self, config, *args):
        super(BattleModifier, self)._initFromConfig(config)
        self.__modificationTree = ModificationTree(config, self.param)

    def _configureParam(self, config):
        paramId = config.name
        if paramId not in BattleParams.ALL:
            raise SoftException('[BattleModifiers] Unknown param {}'.format(paramId))
        return battle_params.g_cache[paramId]

    def _makeDescr(self):
        return (self.param.id, self.gameplayImpact, self.__modificationTree.descr())

    def _makeId(self):
        return hash((self.param.id, self.__modificationTree.id()))


class FakeBattleModifier(ModifierBase):
    __slots__ = ()

    def __repr__(self):
        return 'FakeBattleModifier(descr = {})'.format(self.descr())

    def _initFromDescr(self, descr):
        limitsIdx = 4
        _, packed, value, paramDescr = descr[:limitsIdx]
        self.param = FakeBattleParam(paramDescr)
        self.useType = packed >> 4 & 3
        self.gameplayImpact = packed >> 2 & 3
        self.value = value
        if packed & 2:
            self.minValue = descr[limitsIdx]
            limitsIdx += 1
        if packed & 1:
            self.maxValue = descr[limitsIdx]
        self._descr = descr

    def _initFromConfig(self, config, *args):
        super(FakeBattleModifier, self)._initFromConfig(config)
        self.value = self.__readValue(config)
        self.useType = self.__readUseType(config)
        self.minValue, self.maxValue = self.__readRestrictions(config)

    def _configureParam(self, config):
        if not config.has_key(FAKE_PARAM_NAME):
            raise SoftException('Missing fakeParam section in FakeBattleModifier')
        return FakeBattleParam(config[FAKE_PARAM_NAME])

    def _makeDescr(self):
        packed = self.useType << 4 | self.gameplayImpact << 2
        descr = [self.param.id,
         packed,
         self.value,
         self.param.descr()]
        if self.minValue is not None:
            descr[1] |= 2
            descr.append(self.minValue)
        if self.maxValue is not None:
            descr[1] |= 1
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


class VSEBattleModifier(ModifierBase):
    __slots__ = ()

    def __repr__(self):
        return 'VSEBattleModifier(descr = {})'.format(self.descr())

    def __call__(self, aspect, ctx=None):
        return modifier_appliers.g_cache[self.param.id][self.useType](aspect, self.value, ctx)

    def _initFromDescr(self, descr):
        _, value = descr
        self.value = value
        self.param = self._configureParam()
        self.gameplayImpact = self._configureGameplayImpact()
        self._descr = descr

    def _initFromConfig(self, config, *args):
        super(VSEBattleModifier, self)._initFromConfig(config)
        self.value = modifier_readers.g_cache[self.param.id][self.useType](config['value'])

    def _configureGameplayImpact(self, config=None):
        return GameplayImpact.HIDDEN

    def _configureParam(self, config=None):
        return battle_params.g_cache[BattleParams.VSE_MODIFIER]

    def _makeDescr(self):
        return (self.param.id, self.value)

    def _makeId(self):
        pass


class BattleModifiers(Serializable, battle_modifiers.BattleModifiers):
    __slots__ = ('__modifiers', '__scope', '__domain', '__id')

    def __init__(self, source=None):
        self.__modifiers = OrderedDict()
        self.__scope = 0
        self.__domain = 0
        self.__id = None
        super(BattleModifiers, self).__init__(source)
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
    def retrieveDescr(descr, scope=ModifierScope.FULL):
        if not descr:
            return descr
        res = []
        for modifierDescr in descr:
            if battle_params.g_cache[modifierDescr[0]].scope & scope:
                res.append(modifierDescr)

        return tuple(res)

    @staticmethod
    def getConstantsOriginal():
        return constants_modifications.g_cache.get()

    @staticmethod
    def clearVehicleModifications():
        vehicle_modifications.g_cache.clear()

    @staticmethod
    def clearConstantsModifications():
        constants_modifications.g_cache.clear()

    def get(self, paramId):
        return self.__modifiers.get(paramId)

    def descr(self, scope=ModifierScope.FULL):
        return tuple((modifier.descr() for modifier in self.__modifiers.itervalues() if modifier.param.scope & scope))

    def domain(self):
        return self.__domain

    def haveDomain(self, domain):
        return bool(self.__domain & domain)

    def scope(self):
        return self.__scope

    def haveScope(self, scope):
        return bool(self.__scope & scope)

    def id(self):
        if self.__id is None:
            self.__id = self.__makeId()
        return self.__id

    def getVehicleModification(self, vehType):
        return vehicle_modifications.g_cache.get(vehType, self)

    def getConstantsModification(self):
        return constants_modifications.g_cache.get(self)

    def getVsePlansByAspect(self, aspect):
        return filter(None, [ m(aspect) for m in self.__modifiers.itervalues() if m.param.domain & ModifierDomain.VSE ])

    def _initFromConfig(self, config, *_):
        modifiers = self.__modifiers
        scope = 0
        domain = 0
        fakeModifierIdx = 0
        vseModifierIdx = 0
        for modifierName, modifierSection in config.items():
            if modifierName == 'xmlns:xmlref':
                continue
            if modifierName == BattleParams.FAKE_MODIFIER:
                modifier = FakeBattleModifier(modifierSection)
                modifiers[BattleParams.FAKE_MODIFIER + str(fakeModifierIdx)] = modifier
                scope |= modifier.param.scope
                domain |= modifier.param.domain
                fakeModifierIdx = fakeModifierIdx + 1
                continue
            if modifierName == BattleParams.VSE_MODIFIER:
                modifier = VSEBattleModifier(modifierSection)
                modifiers[BattleParams.VSE_MODIFIER + str(vseModifierIdx)] = modifier
                scope |= modifier.param.scope
                domain |= modifier.param.domain
                vseModifierIdx = vseModifierIdx + 1
                continue
            modifier = BattleModifier(modifierSection)
            if modifier.param.id in modifiers:
                LOG_WARNING('[BattleModifiers] Ignore multiple modifiers for param {}'.format(modifier.param.id))
                continue
            modifiers[modifier.param.id] = modifier
            scope |= modifier.param.scope
            domain |= modifier.param.domain

        self.__scope = scope
        self.__domain = domain

    def _initFromDescr(self, descr):
        modifiers = self.__modifiers
        scope = 0
        domain = 0
        fakeModifierIdx = 0
        vseModifierIdx = 0
        for modifierDescr in descr:
            paramId = modifierDescr[0]
            if paramId == BattleParams.FAKE_MODIFIER:
                modifier = FakeBattleModifier(modifierDescr)
                modifiers[BattleParams.FAKE_MODIFIER + str(fakeModifierIdx)] = modifier
                scope |= modifier.param.scope
                domain |= modifier.param.domain
                fakeModifierIdx = fakeModifierIdx + 1
                continue
            if paramId == BattleParams.VSE_MODIFIER:
                modifier = VSEBattleModifier(modifierDescr)
                modifiers[BattleParams.VSE_MODIFIER + str(vseModifierIdx)] = modifier
                scope |= modifier.param.scope
                domain |= modifier.param.domain
                vseModifierIdx = vseModifierIdx + 1
                continue
            modifier = BattleModifier(modifierDescr)
            modifiers[modifier.param.id] = modifier
            scope |= modifier.param.scope
            domain |= modifier.param.domain

        self.__scope = scope
        self.__domain = domain

    def __makeId(self):
        ids = [ modifier.id() for modifier in self.__modifiers.itervalues() if modifier.hasUniqueID() ]
        return hash(tuple(sorted(ids)))


def getGlobalModifiers():
    global g_cache
    if g_cache is None:
        g_cache = _readGlobalBattleModifiers()
    return g_cache


def _readGlobalBattleModifiers():
    hasGlobalSupport = IS_DEVELOPMENT and (IS_CLIENT or IS_BASEAPP)
    if not hasGlobalSupport:
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
