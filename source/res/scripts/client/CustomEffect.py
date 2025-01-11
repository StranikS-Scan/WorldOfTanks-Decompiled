# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CustomEffect.py
import material_kinds
from items import _xml
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from helpers.PixieNode import EffectNode, TrackEffectNode
from helpers import EffectsList
from soft_exception import SoftException
gNodes = {}
gEffectLists = dict()

def getEffectList(name):
    global gEffectLists
    return gEffectLists.get(name, None)


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

    def getActiveEffects(self, effects, args):
        pass


class DiscreteSelectorDesc(SelectorDesc):
    __slots__ = ('_selectors', '_variable')

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
        newSelectors = dict()
        for key, selector in self._selectors.iteritems():
            selector.fillTemplate(args, effects)
            newKey = args.get(key, key)
            newSelectors[newKey] = selector

        self._selectors = newSelectors

    def getActiveEffects(self, effects, args):
        keyValue = args.get(self._variable, None)
        if keyValue is None:
            return
        else:
            value = self._selectors.get(keyValue, None)
            if value is not None:
                value.getActiveEffects(effects, args)
            return


class MatkindSelectorDesc(DiscreteSelectorDesc):
    __slots__ = ('_variable',)

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
    __slots__ = ('_selectors', '_variable', '__keys')

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
        for i in xrange(len(self.__keys)):
            newKeys.append(args.get(self.__keys[i], self.__keys[i]))
            self._selectors[i].fillTemplate(args, effects)

        self.__keys = tuple(newKeys)

    def getActiveEffects(self, effects, args):
        keyValue = args[self._variable]
        if not keyValue:
            return
        idx = -1
        for leftBound in self.__keys:
            if keyValue < leftBound:
                break
            idx += 1

        if -1 < idx < len(self._selectors):
            self._selectors[idx].getActiveEffects(effects, args)


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

    def getActiveEffects(self, effects, args):
        isPc = args['isPC']
        for selector in self._selectors:
            if selector._isPC is None:
                selector.getActiveEffects(effects, args)
            if selector._isPC == isPc:
                selector.getActiveEffects(effects, args)

        return


class EffectSelectorDesc(SelectorDesc):
    __slots__ = ('__hardPoint', '_id', '__ttl', '_effectList', '_variable')

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
        for key, val in args.iteritems():
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

    def getActiveEffects(self, effects, args):
        effects.add(self._id)

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
    __slots__ = ('_effectList',)

    def __init__(self):
        super(EffectListSelectorDesc, self).__init__()
        self._effectList = True


class EffectDescriptorBase(object):
    __slots__ = ('_selectorDesc',)

    def __init__(self):
        self._selectorDesc = None
        return

    def getActiveEffects(self, effects, args):
        pass


class CustomEffectsDescriptor(EffectDescriptorBase):
    __slots__ = ('__effects', '_selectorDesc')

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
        if 'new_hp_vfx' in args['vehicleTags']:
            return MainTemplateSelector(self, args)
        else:
            return MainCustomSelector(self, args) if self._selectorDesc is not None else None

    def getActiveEffects(self, effects, args):
        if self._selectorDesc is not None:
            self._selectorDesc.getActiveEffects(effects, args)
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

    def create(self, args):
        effectDescriptor = self.__descriptors['default']
        if len(self.__descriptors) > 1:
            for tag in args['engineTags']:
                if tag in self.__descriptors:
                    effectDescriptor = self.__descriptors[tag]
                    break

        return ExhaustMainSelector(effectDescriptor, args, self.nodes) if effectDescriptor is not None else None

    def getActiveEffects(self, effects, args):
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
                    self._destroyNode(node)

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
                        self._deactivateNode(node)

            self._activeEffectId = set()
            return

    def update(self, args):
        if not self._enabled:
            return
        activeEffects = set()
        self._effectSelector.getActiveEffects(activeEffects, args)
        disableEffects = self._activeEffectId.difference(activeEffects)
        for effect in disableEffects:
            self.enable(effect, False)

        enableEffects = self._getNewEffects(activeEffects)
        for effect in enableEffects:
            self.enable(effect, True)

        self._activeEffectId = activeEffects

    def _getNewEffects(self, effects):
        return effects.difference(self._activeEffectId)

    def _destroyNode(self, node):
        node.destroy()

    def _deactivateNode(self, node):
        node.deactivate()

    def _activateNode(self, node):
        node.activate()


class MainCustomSelector(MainSelectorBase):

    def __init__(self, selectorDesc, args):
        super(MainCustomSelector, self).__init__(selectorDesc, args)
        self.__createEffects(self._effectSelector.effects, args)

    def settingsFlags(self):
        return EffectSettings.SETTING_DUST

    def __createEffects(self, effects, args):
        self._effectNodes = dict()
        for nodeName, nodeDesc in effects.iteritems():
            modelName = nodeDesc[1]
            model = args[modelName]['model']
            try:
                node = model.node(nodeName)
                if node is None and any((i in args['vehicleTags'] for i in ('wheeledVehicle', 'wheeledVehicleWithoutFeatures'))):
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


class MainTemplateSelector(MainSelectorBase):
    METADATA_SPLITTER = '__'
    TYPE_SPLITTER = '_'
    HP_PREFIX = 'HP_'
    NODE_TYPES_MAPPING = {'track': TrackEffectNode}

    def __init__(self, selectorDesc, args):
        super(MainTemplateSelector, self).__init__(selectorDesc, args)
        self.__createEffects(self._effectSelector.effects, args)

    def settingsFlags(self):
        return EffectSettings.SETTING_DUST

    @property
    def effectNodes(self):
        result = []
        for items in self._effectNodes.values():
            result.extend(items)

        return result

    def enable(self, effectID, enable):
        nodes = self._effectNodes.get(effectID[0], None)
        if nodes is None:
            return
        else:
            for node in nodes:
                node.enable(effectID[1], enable)

            return

    def __createEffects(self, effects, args):
        templateNodes = self.__getTemplateNodes(effects, args)
        self._effectNodes = dict()
        for nodeName, nodeDesc in effects.iteritems():
            try:
                effectId = nodeDesc[0]
                effectNodes = self.__extractEffects(nodeName, nodeDesc, args, templateNodes)
                self._effectNodes[effectId] = effectNodes
            except Exception:
                LOG_ERROR('Node %s is not found' % nodeName)
                continue

    def _destroyNode(self, nodes):
        for node in nodes:
            node.destroy()

    def _deactivateNode(self, nodes):
        for node in nodes:
            node.deactivate()

    def _activateNode(self, nodes):
        for node in nodes:
            node.activate()

    def _getNewEffects(self, effects):
        return effects

    def __extractEffects(self, nodeName, nodeDesc, args, templateNodes):
        drawOrderBase = args.get('drawOrderBase', 0)
        appearance = args.get('appearance')
        modelName = nodeDesc[1]
        waterY = nodeDesc[2]
        drawOrder = drawOrderBase + nodeDesc[3]
        effects = nodeDesc[4]
        model = args[modelName]['model']
        if nodeName not in templateNodes:
            return [EffectNode(model, nodeName, waterY, drawOrder, effects)]
        effectNodes = []
        for nodeData in templateNodes[nodeName]:
            templateNodeName, nodeType, metaData = nodeData
            effectCls = self.NODE_TYPES_MAPPING[nodeType]
            node = effectCls(model, templateNodeName, waterY, drawOrder, effects, appearance, metaData)
            effectNodes.append(node)

        return effectNodes

    def __getTemplateNodes(self, effects, args):
        modelNames = set()
        templateNodes = dict()
        for nodeDesc in effects.itervalues():
            modelName = nodeDesc[1]
            if modelName in modelNames:
                continue
            modelNames.add(modelName)
            model = args[modelName]['model']
            self.__extractHardPoints(model.getNodeNames(), templateNodes)

        return templateNodes

    def __extractHardPoints(self, nodeNames, templateNodes):
        for nodeName in nodeNames:
            if not nodeName.startswith(self.HP_PREFIX) or self.METADATA_SPLITTER not in nodeName:
                continue
            hardPoint, metaData, nodeType = self.__extractNodeParts(nodeName)
            if not hardPoint or not metaData or not nodeType:
                continue
            templateNodes.setdefault(hardPoint, []).append((nodeName, nodeType, metaData))

    def __extractNodeParts(self, nodeName):
        nodeData = nodeName.split(self.METADATA_SPLITTER)
        if len(nodeData) != 2:
            LOG_ERROR('Node %s has invalid format. {HARD_POINT}:{META_DATA} required' % nodeName)
            return (None, None, None)
        hardPoint, metaData = nodeData
        nodeData = metaData.split(self.TYPE_SPLITTER, 1)
        if len(nodeData) != 2:
            LOG_ERROR('Node %s has invalid metadata format.{TYPE}_{DATA} required' % nodeName)
            return (None, None, None)
        nodeType = nodeData[0]
        if nodeType not in self.NODE_TYPES_MAPPING:
            LOG_ERROR('Node %s has invalid type %s.' % (nodeName, nodeType))
            return (None, None, None)
        else:
            return (hardPoint, metaData, nodeType)


class ExhaustMainSelector(MainSelectorBase):

    def __init__(self, selectorDesc, args, nodes):
        super(ExhaustMainSelector, self).__init__(selectorDesc, args)
        self.__createEffects(selectorDesc.effects, args, nodes)

    def settingsFlags(self):
        return EffectSettings.SETTING_EXHAUST

    def __createEffects(self, effects, args, nodes):
        self._effectNodes = dict()
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
