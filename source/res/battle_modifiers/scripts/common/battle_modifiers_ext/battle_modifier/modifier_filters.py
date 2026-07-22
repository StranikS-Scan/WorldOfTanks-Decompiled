# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/battle_modifier/modifier_filters.py
from typing import TYPE_CHECKING, Optional, Any, Tuple, Union, List, Dict
from battle_modifiers_ext.battle_params import BattleParam
from battle_modifiers_ext.battle_modifier import modifier_readers
from battle_modifiers_ext.battle_modifier import modifier_appliers
from battle_modifiers_ext.battle_modifier.modifier_restrictions import readRestrictions, getValueLimiter
from battle_modifiers_ext.battle_modifier.modifier_helpers import createLevelTag, parseLevelTag
from battle_modifiers_ext.constants_ext import DEBUG_MODIFIERS, ERROR_TEMPLATE, UseType, ModifierRestriction, NodeType, ShellKind
from constants import ROLE_TYPE_TO_LABEL, ROLE_LABEL_TO_TYPE, VEHICLE_CLASSES, MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from debug_utils import LOG_DEBUG
from ResMgr import DataSection
from soft_exception import SoftException
if TYPE_CHECKING:
    from battle_modifiers_common import ModifiersContext
    from items.vehicles import VehicleType
    from items.vehicle_items import Shell

class ModificationNode(object):
    __slots__ = ('param', 'useType', 'value', 'minValue', 'maxValue', '__descr', '__id', '__valueLimiter')

    def __init__(self, source, param):
        self.param = param
        self.minValue = None
        self.maxValue = None
        self.__descr = None
        self.__id = None
        self.__valueLimiter = None
        if isinstance(source, DataSection):
            self.__readConfig(source)
        else:
            self.__initFromDescr(source)
        return

    def __call__(self, value, ctx=None):
        modifiedValue = modifier_appliers.g_cache[self.param.id][self.useType](value, self.value, ctx)
        if self.__valueLimiter:
            modifiedValue = self.__valueLimiter(modifiedValue)
        if DEBUG_MODIFIERS:
            LOG_DEBUG("[BattleModifiers][Debug] Apply modifier '{}' ({} {}, min {}, max {}): {} -> {}".format(self.param.name, UseType.ID_TO_NAME[self.useType], self.value, self.minValue if self.minValue is not None else self.param.minValue, self.maxValue if self.maxValue is not None else self.param.maxValue, value, modifiedValue))
        return modifiedValue

    def __hash__(self):
        return self.id()

    def __repr__(self):
        return 'ModificationNode(value = {}, useTypeName = {}, minValue = {}, maxValue = {})'.format(self.value, UseType.ID_TO_NAME[self.useType], self.minValue, self.maxValue)

    def descr(self):
        if self.__descr is None:
            self.__descr = self.__makeDescr()
        return self.__descr

    def id(self):
        if self.__id is None:
            self.__id = self.__makeId()
        return self.__id

    def __initFromDescr(self, descr):
        limitsIdx = 2
        packed, value = descr[:limitsIdx]
        self.useType = packed >> 2 & 3
        self.value = value
        minValue = None
        maxValue = None
        if packed & 2:
            minValue = descr[limitsIdx]
            limitsIdx += 1
        if packed & 1:
            maxValue = descr[limitsIdx]
        self.__setLimits(minValue, maxValue)
        self.__descr = descr
        return

    def __readConfig(self, config):
        self.useType = self.__readUseType(config)
        self.value = self.__readValue(config)
        self.__applyRestrictions(config)

    def __makeDescr(self):
        packed = self.useType << 2
        descr = [packed, self.value]
        if self.minValue is not None:
            descr[0] |= 2
            descr.append(self.minValue)
        if self.maxValue is not None:
            descr[0] |= 1
            descr.append(self.maxValue)
        return tuple(descr)

    def __makeId(self):
        return hash(self.descr())

    def __setLimits(self, minValue, maxValue):
        self.minValue = minValue
        self.maxValue = maxValue
        self.__valueLimiter = getValueLimiter(minValue if minValue is not None else self.param.minValue, maxValue if maxValue is not None else self.param.maxValue)
        return

    def __readValue(self, config):
        if not config.has_key('value'):
            raise SoftException(ERROR_TEMPLATE.format('Missing value', config.name))
        return modifier_readers.g_cache[self.param.id][self.useType](config['value'])

    def __readUseType(self, config):
        if not config.has_key('useType'):
            raise SoftException(ERROR_TEMPLATE.format('Missing use type', config.name))
        useTypeName = config['useType'].asString
        if useTypeName not in UseType.NAMES:
            raise SoftException("[BattleModifiers] Unknown use type '{}'".format(useTypeName))
        return UseType.NAME_TO_ID[useTypeName]

    def __applyRestrictions(self, config):
        param = self.param
        localValidators, localMinValue, localMaxValue = readRestrictions(config, self.param.id, ModifierRestriction.LIMITS)
        if localMinValue is not None and param.minValue is not None and localMinValue < param.minValue:
            raise SoftException(ERROR_TEMPLATE.format('Global min limit is violated by local min limit', config.name))
        if localMaxValue is not None and param.maxValue is not None and localMaxValue > param.maxValue:
            raise SoftException(ERROR_TEMPLATE.format('Global max limit is violated by local max limit', config.name))
        resValidators = param.validators.copy()
        resValidators.update(localValidators)
        for validator in resValidators.itervalues():
            validator(self)

        if self.useType != UseType.VAL:
            self.__setLimits(localMinValue, localMaxValue)
        return


class ModificationTree(object):
    __slots__ = ('param', 'nodes', '__descr', '__id')

    def __init__(self, source, param):
        self.param = param
        self.__descr = None
        self.__id = None
        if isinstance(source, DataSection):
            self.__readConfig(source)
        else:
            self.__initFromDescr(source)
        return

    def __call__(self, value, ctx=None):
        vehType = ctx.vehicle if ctx is not None else None
        shellDescr = ctx.shell if ctx is not None else None
        modificationNode = self.__retrieveModificationNode(vehType, shellDescr)
        return value if not modificationNode else modificationNode(value, ctx)

    def __hash__(self):
        return self.id()

    def __repr__(self):
        return 'ModificationTree({})'.format(self.__descr)

    def descr(self):
        return self.__descr

    def id(self):
        if self.__id is None:
            self.__id = self.__makeId()
        return self.__id

    def __initFromDescr(self, descr):
        resDict = {}
        for node in descr:
            nodeType = node[0]
            if nodeType == NodeType.ROOT:
                self.__parseRootNode(node, resDict)
            if nodeType == NodeType.SHELL:
                self.__parseShellNode(node, resDict)
            if nodeType == NodeType.VEHICLE:
                self.__parseVehicleNode(node, resDict)

        self.nodes = resDict
        self.__descr = descr

    def __parseRootNode(self, descr, accDict):
        _, nodeDescr = descr
        accDict[NodeType.ROOT] = ModificationNode(nodeDescr, self.param)

    def __parseShellNode(self, descr, accDict):
        _, shellKeys, nodeDescr = descr
        modificationNode = ModificationNode(nodeDescr, self.param)
        accDict.update(dict(((key, modificationNode) for key in shellKeys)))

    def __parseVehicleNode(self, descr, accDict):
        _, vehicleKeys = descr[:2]
        vehicleDict = {}
        for node in descr[2:]:
            nodeType = node[0]
            if nodeType == NodeType.ROOT:
                self.__parseRootNode(node, vehicleDict)
            if nodeType == NodeType.SHELL:
                self.__parseShellNode(node, vehicleDict)

        accDict.update(dict(((key, vehicleDict) for key in vehicleKeys)))

    def __readConfig(self, config):
        resDict = {}
        resDescr = []
        self.__readRootNode(config, resDict, resDescr)
        self.__readNodes(config, NodeType.SHELL, resDict, resDescr)
        self.__readNodes(config, NodeType.VEHICLE, resDict, resDescr)
        if not resDict:
            raise SoftException(ERROR_TEMPLATE.format('Invalid modifier', self.param.name))
        self.nodes = resDict
        self.__descr = tuple(resDescr)

    def __readNodes(self, config, nodeType, accDict, accDescr):
        if not config.has_key(nodeType):
            return
        if not self.param.domain & NodeType.SUPPORTED_DOMAINS[nodeType]:
            raise SoftException(ERROR_TEMPLATE.format("'{}' filters can't be used".format(nodeType), self.param.name))
        if nodeType == NodeType.SHELL:
            reader = self.__readShellNode
        elif nodeType == NodeType.VEHICLE:
            reader = self.__readVehicleNode
        else:
            raise SoftException("[BattleModifiers] Node type '{}' is unsupported for list reading".format(nodeType))
        for sectionName, section in config.items():
            if sectionName == nodeType:
                reader(section, accDict, accDescr)

    def __readModificationNode(self, config):
        return None if not config.has_key('value') and not config.has_key('useType') else ModificationNode(config, self.param)

    def __readRootNode(self, config, accDict, accDescr):
        rootNode = self.__readModificationNode(config)
        if rootNode:
            accDict[NodeType.ROOT] = rootNode
            accDescr.append((NodeType.ROOT, rootNode.descr()))

    def __readShellNode(self, config, accDict, accDescr):
        if not config.has_key('filter'):
            raise SoftException(ERROR_TEMPLATE.format('Shell node should contain filter', self.param.name))
        filterSection = config['filter']
        shellKeys = []
        if filterSection.has_key('regular'):
            shellKeys += self.__readShellFilterKeys(filterSection['regular'], False)
        if filterSection.has_key('improved'):
            shellKeys += self.__readShellFilterKeys(filterSection['improved'], True)
        if not shellKeys:
            raise SoftException(ERROR_TEMPLATE.format('Some filter keys should be provided for shell node', self.param.name))
        shellNode = self.__readModificationNode(config)
        if not shellNode:
            raise SoftException(ERROR_TEMPLATE.format('Shell node should contain root part', self.param.name))
        accDict.update(dict(((key, shellNode) for key in shellKeys)))
        accDescr.append((NodeType.SHELL, tuple(shellKeys), shellNode.descr()))

    def __readShellFilterKeys(self, config, isImproved):
        keys = config.asString.split()
        if len(keys) == 1 and keys[0] == ShellKind.ALL_KEY:
            return list(ShellKind.ALL_IMPROVED if isImproved else ShellKind.ALL_REGULAR)
        for key in keys:
            if key not in ShellKind.ALL_REGULAR:
                raise SoftException(ERROR_TEMPLATE.format("Unknown shell filter key '{}'".format(key), self.param.name))

        if isImproved:
            return [ key + ShellKind.IMPROVED_POSTFIX for key in keys ]
        return keys

    def __readVehicleNode(self, config, accDict, accDescr):
        if not config.has_key('filter'):
            raise SoftException(ERROR_TEMPLATE.format('Vehicle node should contain filter', self.param.name))
        vehiclKeys = self.__readVehicleFilterKeys(config['filter'])
        if not vehiclKeys:
            raise SoftException(ERROR_TEMPLATE.format('Some filter keys should be provided for vehicle node', self.param.name))
        vehicleDict = {}
        vehicleDescr = [NodeType.VEHICLE, tuple(vehiclKeys)]
        self.__readRootNode(config, vehicleDict, vehicleDescr)
        self.__readNodes(config, NodeType.SHELL, vehicleDict, vehicleDescr)
        if not vehicleDict:
            raise SoftException(ERROR_TEMPLATE.format('Invalid vehicle node', self.param.name))
        accDict.update(dict(((key, vehicleDict) for key in vehiclKeys)))
        accDescr.append(tuple(vehicleDescr))

    def __readVehicleFilterKeys(self, config):
        from items.vehicles import g_list
        keys = config.asString.split()
        for key in keys:
            if g_list.isVehicleExisting(key) or key in ROLE_LABEL_TO_TYPE or key in VEHICLE_CLASSES:
                continue
            level = parseLevelTag(key)
            if (level is not None and MIN_VEHICLE_LEVEL) <= level <= MAX_VEHICLE_LEVEL:
                continue
            raise SoftException(ERROR_TEMPLATE.format("Unknown vehicle filter key '{}'".format(key), self.param.name))

        return keys

    def __retrieveModificationNode(self, vehType=None, shellDescr=None):
        nodes = self.nodes
        targetNode = nodes
        if vehType:
            roleTag = ROLE_TYPE_TO_LABEL[vehType.role]
            levelTag = createLevelTag(vehType.level)
            if vehType.name in nodes:
                targetNode = nodes[vehType.name]
            elif roleTag in nodes:
                targetNode = nodes[roleTag]
            elif vehType.classTag in nodes:
                targetNode = nodes[vehType.classTag]
            elif levelTag in nodes:
                targetNode = nodes[levelTag]
        if shellDescr:
            shellKey = ShellKind.get(shellDescr)
            if shellKey in targetNode:
                return targetNode[shellKey]
        return targetNode.get(NodeType.ROOT)

    def __makeId(self):
        ids = []
        for key, value in self.nodes.iteritems():
            if isinstance(value, dict):
                for subKey, subValue in value.iteritems():
                    ids.append(hash((key + subKey, subValue)))

            ids.append(hash((key, value)))

        ids.sort()
        return hash(tuple(ids))
