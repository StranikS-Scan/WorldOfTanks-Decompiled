# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CustomEffect.py
from __future__ import absolute_import
from future.utils import viewitems
from past.builtins import intern, xrange
import material_kinds
from items import _xml
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from helpers.PixieNode import EffectNode
from helpers import EffectsList
from soft_exception import SoftException
gNodes = {}
gEffectLists = {}

def getEffectList(name):
    global gEffectLists
    return gEffectLists.get(name)


def setEffectList(data):
    global gEffectLists
    gEffectLists = data


class RangeTable(object):

    def __init__(self, keys, values):
        self.keys = keys
        self.values = values

    def lookup(self, point, defaultValue=None):
        foundValue = defaultValue
        idx = -1
        for leftBound in self.keys:
            if point < leftBound:
                break
            idx += 1

        return foundValue if idx == -1 or len(self.values) <= idx else self.values[idx]


class SelectorDescFactory(object):

    @staticmethod
    def initFactory(section):
        SelectorDescFactory.readNodes(section)
        SelectorDescFactory.readEffectLists(section)

    @staticmethod
    def releseFactory():
        global gNodes
        gNodes.clear()

    @staticmethod
    def readEffectLists(dataSection):
        try:
            section = dataSection['effectLists']
            if section is None:
                return
            for effectList in section.items():
                name = effectList[0]
                gEffectLists[name] = EffectsList.effectsFromSection(effectList[1])

        except Exception:
            LOG_CURRENT_EXCEPTION()

        return

    @staticmethod
    def readNodes(dataSection):
        gNodes.clear()
        try:
            section = dataSection['nodes']
            if section is None:
                return
            for node in section.items():
                nodeName = node[1].readString('name', '')
                modelName = node[1].readString('model', '')
                waterY = node[1].readBool('waterY', False)
                drawOrder = node[1].readInt('drawOrder', 0)
                gNodes[nodeName] = (modelName, waterY, drawOrder)

        except Exception:
            LOG_CURRENT_EXCEPTION()

        return

    @staticmethod
    def create(selectorDesc, effects=None):
        selectorType = selectorDesc.readString('type')
        selector = None
        if selectorType == 'discrete':
            selector = DiscreteSelectorDesc()
        elif selectorType == 'range':
            selector = RangeSelectorDesc()
        elif selectorType == 'effect':
            selector = EffectSelectorDesc()
        elif selectorType == 'effectList':
            selector = EffectListSelectorDesc()
        elif selectorType == 'matkind':
            selector = MatkindSelectorDesc()
        elif selectorType == 'union':
            selector = UnionSelectorDesc()
        if selector is not None:
            selector.read(selectorDesc, effects)
        return selector


def makeDescVariable(templateVar, args):
    templateVarSplit = templateVar.split(':')
    if len(templateVarSplit) == 2:
        templVarName = templateVarSplit[0]
        varName = args.get(templVarName, templVarName)
        return varName + ':' + templateVarSplit[1]
    return args.get(templateVar, templateVar)


class SelectorDesc(object):
    __slots__ = ('_variable', '_isPC')

    def __init__(self):
        self._variable = None
        self._isPC = None
        return

    def read(self, dataSection, effects):
        isPC = dataSection['isPC']
        self._isPC = isPC.asBool if isPC is not None else None
        return

    def fillTemplate(self, args, effects):
        pass

    def getActiveEffects(self, effects, args, resetEffectArgs=None):
        pass


class DiscreteSelectorDesc(SelectorDesc):
    __slots__ = ('_selectors',)

    @property
    def selectors(self):
        return self._selectors

    def __init__(self):
        super(DiscreteSelectorDesc, self).__init__()
        self._selectors = {}

    def read(self, dataSection, effects):
        super(DiscreteSelectorDesc, self).read(dataSection, effects)
        self._variable = dataSection['variable'].asString.strip()
        for selectorDesc in dataSection.items():
            if selectorDesc[0] == 'selector':
                value = selectorDesc[1]['key'].asString.strip()
                try:
                    value = float(value)
                except Exception:
                    pass

                self._selectors[value] = SelectorDescFactory.create(selectorDesc[1], effects)

    def fillTemplate(self, args, effects):
        self._variable = makeDescVariable(self._variable, args)
        newSelectors = {}
        for key, selector in viewitems(self._selectors):
            selector.fillTemplate(args, effects)
            newKey = args.get(key, key)
            newSelectors[newKey] = selector

        self._selectors = newSelectors

    def getActiveEffects(self, effects, args, resetEffectArgs=None):
        keyValue = args.get(self._variable, None)
        if keyValue is None:
            return
        else:
            value = self._selectors.get(keyValue, None)
            if value is not None:
                if resetEffectArgs is not None and self._variable in resetEffectArgs:
                    value.getActiveEffects(resetEffectArgs[self._variable], args)
                value.getActiveEffects(effects, args, resetEffectArgs)
            return


class MatkindSelectorDesc(DiscreteSelectorDesc):
    __slots__ = ()

    def read(self, dataSection, effects):
        SelectorDesc.read(self, dataSection, effects)
        self._variable = dataSection['variable'].asString.strip()
        for selectorDesc in dataSection.items():
            if selectorDesc[0] == 'selector':
                matkindName = selectorDesc[1]['key'].asString.strip()
                matkindList = material_kinds.EFFECT_MATERIAL_IDS_BY_NAMES.get(matkindName)
                selector = SelectorDescFactory.create(selectorDesc[1], effects)
                for matKind in matkindList:
                    self._selectors[matKind] = selector


class RangeSelectorDesc(SelectorDesc):
    __slots__ = ('_selectors', '__keys')

    def __init__(self):
        super(RangeSelectorDesc, self).__init__()
        self._selectors = None
        self.__keys = None
        return

    def read(self, dataSection, effects):
        super(RangeSelectorDesc, self).read(dataSection, effects)
        keys = []
        values = []
        self._variable = dataSection['variable'].asString.strip()
        for selectorDesc in dataSection.items():
            if selectorDesc[0] == 'selector':
                value = selectorDesc[1]['key'].asString.strip()
                try:
                    value = float(value)
                except Exception:
                    pass

                keys.append(value)
                values.append(SelectorDescFactory.create(selectorDesc[1], effects))

        self.__keys = tuple(keys)
        self._selectors = tuple(values)

    def fillTemplate(self, args, effects):
        self._variable = makeDescVariable(self._variable, args)
        newKeys = []
        for i, key in enumerate(self.__keys):
            newKeys.append(args.get(key, key))
            self._selectors[i].fillTemplate(args, effects)

        self.__keys = tuple(newKeys)

    def getActiveEffects(self, effects, args, resetEffectArgs=None):
        keyValue = args[self._variable]
        if not keyValue:
            return
        else:
            idx = -1
            for leftBound in self.__keys:
                if keyValue < leftBound:
                    break
                idx += 1

            if -1 < idx < len(self._selectors):
                if resetEffectArgs is not None and self._variable in resetEffectArgs:
                    self._selectors[idx].getActiveEffects(resetEffectArgs[self._variable], args)
                self._selectors[idx].getActiveEffects(effects, args, resetEffectArgs)
            return


class UnionSelectorDesc(SelectorDesc):
    __slots__ = ('_selectors',)

    def __init__(self):
        super(UnionSelectorDesc, self).__init__()
        self._selectors = None
        return

    def read(self, dataSection, effects):
        super(UnionSelectorDesc, self).read(dataSection, effects)
        self._selectors = []
        for selectorDesc in dataSection.items():
            if selectorDesc[0] == 'selector':
                self._selectors.append(SelectorDescFactory.create(selectorDesc[1], effects))

    def fillTemplate(self, args, effects):
        for selector in self._selectors:
            selector.fillTemplate(args, effects)

    def getActiveEffects(self, effects, args, resetEffectArgs=None):
        isPc = args['isPC']
        for selector in self._selectors:
            if selector._isPC is None or selector._isPC == isPc:
                selector.getActiveEffects(effects, args, resetEffectArgs)

        return


class EffectSelectorDesc(SelectorDesc):
    __slots__ = ('__hardPoint', '_id', '__ttl', '_effectList')

    @property
    def isEffectList(self):
        return self._effectList is True

    def __init__(self):
        super(EffectSelectorDesc, self).__init__()
        self.__hardPoint = None
        self._id = None
        self.__ttl = 0.0
        self._effectList = False
        return

    def read(self, dataSection, effects):
        self._variable = intern(dataSection['name'].asString.strip())
        self.__hardPoint = dataSection['effectHP']
        ttlSection = dataSection['ttl']
        if self.__hardPoint is not None:
            self.__hardPoint = self.__hardPoint.asString.strip()
        if ttlSection is not None:
            ttlSection = ttlSection.asString.strip()
            try:
                self.__ttl = float(ttlSection)
            except Exception:
                pass

        if self.__hardPoint is not None:
            self.__makeIdWithHP(effects)
        else:
            self.__makeId(effects)
        return

    def fillTemplate(self, args, effects):
        self._variable = makeDescVariable(self._variable, args)
        self.__ttl = args.get(self.__ttl, self.__ttl)
        pathArgs = []
        for key, val in viewitems(args):
            if len(key) == 2 and key[0] == '_' and key[1].isdigit:
                index = int(key[1])
                if index >= len(pathArgs):
                    for i in xrange(index - len(pathArgs) + 1):
                        pathArgs.append('{' + str(i) + '}')

                pathArgs[index] = val

        if pathArgs:
            self._variable = self._variable.format(*pathArgs)
        if self.__hardPoint is not None:
            self.__hardPoint = args.get(self.__hardPoint, self.__hardPoint)
            self.__makeIdWithHP(effects)
        else:
            self.__makeId(effects)
        return

    def getActiveEffects(self, effects, args, resetEffectArgs=None):
        effects.add(self._id)
        if resetEffectArgs is not None and self._variable in resetEffectArgs:
            resetEffectArgs[self._variable].add(self._id)
        return

    def __makeId(self, effects):
        if effects is not None:
            effectID = effects.get(self._variable, None)
            if effectID is None:
                effectID = len(effects)
                effects[self._variable] = (effectID, self.__ttl, self._effectList)
            else:
                effectID = effectID[EffectNode.EFFECT_ID]
            self._id = effectID
        return

    def __makeIdWithHP(self, effects):
        if effects is not None:
            nodeDesc = gNodes.get(self.__hardPoint, None)
            waterY = False
            drawOrder = 0
            if nodeDesc is not None:
                nodeName = self.__hardPoint
                modelName = nodeDesc[0]
                waterY = nodeDesc[1]
                drawOrder = nodeDesc[2]
            else:
                nodeInf = self.__hardPoint.split('|')
                nodeName = nodeInf[0].strip()
                modelName = nodeDesc[1].strip()
            nodeEffects = effects.get(nodeName, None)
            if nodeEffects is None:
                self._id = len(effects)
                nodeEffects = (self._id,
                 modelName,
                 waterY,
                 drawOrder,
                 {})
                effects[nodeName] = nodeEffects
            else:
                self._id = nodeEffects[0]
            effectID = nodeEffects[4].get(self._variable, None)
            if effectID is None:
                effectID = len(nodeEffects[4])
                nodeEffects[4][self._variable] = (effectID, self.__ttl, self._effectList)
            else:
                effectID = effectID[EffectNode.EFFECT_ID]
            self._id = (self._id, effectID)
        return


class EffectListSelectorDesc(EffectSelectorDesc):
    __slots__ = ()

    def __init__(self):
        super(EffectListSelectorDesc, self).__init__()
        self._effectList = True


class EffectDescriptorBase(object):
    __slots__ = ('_selectorDesc',)

    def __init__(self):
        self._selectorDesc = None
        return

    def getActiveEffects(self, effects, args, resetEffectArgs):
        pass


class CustomEffectsDescriptor(EffectDescriptorBase):
    __slots__ = ('__effects',)

    @staticmethod
    def getDescriptor(dataSection, customDescriptors, xmlCtx, name):
        effectName = intern(_xml.readNonEmptyString(xmlCtx, dataSection, name))
        effectDesc = None
        if effectName is not None:
            effectDesc = customDescriptors.get(effectName, None)
        if effectDesc is None:
            effectDesc = customDescriptors.get('default', None)
        return effectDesc

    @property
    def effects(self):
        return self.__effects

    def __init__(self, dataSection):
        super(CustomEffectsDescriptor, self).__init__()
        try:
            self.__effects = {}
            self._selectorDesc = SelectorDescFactory.create(dataSection['selector'], self.__effects)
        except Exception:
            LOG_CURRENT_EXCEPTION()

    def destroy(self):
        if self._selectorDesc is not None:
            self._selectorDesc.destroy()
        return

    def create(self, args):
        return MainCustomSelector(self, args) if self._selectorDesc is not None else None

    def getActiveEffects(self, effects, args, resetEffectArgs):
        if self._selectorDesc is not None:
            self._selectorDesc.getActiveEffects(effects, args, resetEffectArgs)
        return


class ExhaustEffectDescriptor(EffectDescriptorBase):
    __slots__ = ('__descriptors', 'nodes')

    def __init__(self, dataSection, xmlCtx, customDescriptors, name):
        super(ExhaustEffectDescriptor, self).__init__()
        self.__descriptors = customDescriptors
        self.nodes = [ intern(node) for node in _xml.readNonEmptyString(xmlCtx, dataSection, name).split() ]

    @property
    def descriptors(self):
        return self.__descriptors

    @descriptors.setter
    def descriptors(self, value):
        self.__descriptors = value

    def create(self, args):
        effectDescriptor = self.__descriptors['default']
        if len(self.__descriptors) > 1:
            for tag in args['engineTags']:
                if tag in self.__descriptors:
                    effectDescriptor = self.__descriptors[tag]
                    break

        return ExhaustMainSelector(effectDescriptor, args, self.nodes) if effectDescriptor is not None else None

    def getActiveEffects(self, effects, args, resetEffectArgs):
        raise SoftException('This function should not be called by hand.')


class EffectSettings(object):
    SETTINGS_NO = 0
    SETTING_DUST = 1
    SETTING_EXHAUST = 2


class MainSelectorBase(object):

    @property
    def effectNodes(self):
        return self._effectNodes.values()

    def __init__(self, selectorDesc, args):
        self._activeEffectId = set()
        self._effectSelector = selectorDesc
        self._effectNodes = None
        self._enabled = True
        return

    def destroy(self):
        if self._effectNodes is not None:
            for node in self._effectNodes.values():
                if node is not None:
                    node.destroy()

            self._effectNodes = None
        return

    def settingsFlags(self):
        return EffectSettings.SETTINGS_NO

    def enable(self, effectID, enable):
        pass

    def start(self):
        self._enabled = True

    def stop(self):
        if not self._enabled:
            return
        else:
            self._enabled = False
            for effect in self._activeEffectId:
                self.enable(effect, False)

            if self._effectNodes is not None:
                for node in self._effectNodes.values():
                    if node is not None:
                        node.deactivate()

            self._activeEffectId = set()
            return

    def update(self, args, effectsToReset):
        if not self._enabled:
            return
        else:
            resetEffectArgs = None
            if effectsToReset:
                resetEffectArgs = {varName:set() for varName in effectsToReset}
            activeEffects = set()
            self._effectSelector.getActiveEffects(activeEffects, args, resetEffectArgs)
            if resetEffectArgs:
                self.__resetEffects(resetEffectArgs)
            disableEffects = self._activeEffectId.difference(activeEffects)
            for effect in disableEffects:
                self.enable(effect, False)

            enableEffects = activeEffects.difference(self._activeEffectId)
            for effect in enableEffects:
                self.enable(effect, True)

            self._activeEffectId = activeEffects
            return

    def __resetEffects(self, resetEffectArgs):
        for _, effectIds in resetEffectArgs.items():
            for effId in effectIds:
                if effId in self._activeEffectId:
                    self.enable(effId, False)
                    self._activeEffectId.remove(effId)


class MainCustomSelector(MainSelectorBase):

    def __init__(self, selectorDesc, args):
        super(MainCustomSelector, self).__init__(selectorDesc, args)
        self.__createEffects(self._effectSelector.effects, args)

    def settingsFlags(self):
        return EffectSettings.SETTING_DUST

    def __createEffects(self, effects, args):
        self._effectNodes = {}
        for nodeName, nodeDesc in viewitems(effects):
            modelName = nodeDesc[1]
            model = args[modelName]['model']
            try:
                node = model.node(nodeName)
                if node is None and 'wheeledVehicle' in args['vehicleTags']:
                    continue
                drawOrderBase = args.get('drawOrderBase', 0)
                self._effectNodes[nodeDesc[0]] = EffectNode(model, nodeName, nodeDesc[2], drawOrderBase + nodeDesc[3], nodeDesc[4])
            except Exception:
                LOG_ERROR('Node %s is not found' % nodeName)
                continue

        return

    def enable(self, effectID, enable):
        node = self._effectNodes.get(effectID[0], None)
        if node is not None:
            node.enable(effectID[1], enable)
        return


class ExhaustMainSelector(MainSelectorBase):

    def __init__(self, selectorDesc, args, nodes):
        super(ExhaustMainSelector, self).__init__(selectorDesc, args)
        self.__createEffects(selectorDesc.effects, args, nodes)

    def settingsFlags(self):
        return EffectSettings.SETTING_EXHAUST

    def __createEffects(self, effects, args, nodes):
        self._effectNodes = {}
        for nodeName in nodes:
            model = args['hull']['model']
            try:
                drawOrderBase = args.get('drawOrderBase', 0)
                self._effectNodes[nodeName] = EffectNode(model, nodeName, False, drawOrderBase, self._effectSelector.effects)
            except Exception:
                LOG_ERROR('Node %s is not found' % nodeName)
                continue

    def enable(self, effectID, enable):
        for node in self._effectNodes.values():
            node.enable(effectID, enable)
