# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CustomEffect.py
import BigWorld
import copy
import Math
import material_kinds
from items import _xml
from functools import partial
from debug_utils import *
import weakref
from helpers.PixieBG import PixieBG
gTemplates = None
gNodes = None
gConstantGroup = None

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


class PixieNode(object):
    _PIXIE_NAME = 0
    _PIXIE_ENABLED = 1
    _PIXIE_REF = 2
    _PIXIE_TTL = 3

    def __init__(self, node, waterY, drawOrder, effects):
        self.__node = node
        self.__nodeDefaultLocalTranslation = Math.Matrix(self.__node.local).translation
        self.__drawOrder = drawOrder
        self.__waterY = waterY
        self.__effects = dict()
        self.__ttlCallbacks = dict()
        for effectName, effectDesc in effects.iteritems():
            self.__effects[effectDesc[0]] = [effectName,
             False,
             None,
             effectDesc[1]]

        return

    def destroy(self):
        for cbkId in self.__ttlCallbacks.values():
            if cbkId is not None:
                BigWorld.cancelCallback(cbkId)

        for effectDesc in self.__effects.values():
            if effectDesc[PixieNode._PIXIE_REF] is not None:
                self.__detach(effectDesc)

        self.__effects = None
        self.__ttlCallbacks = None
        return

    def __attach(self, pixie):
        self.__node.attach(pixie)
        pixie.drawOrder = self.__drawOrder
        PixieBG.enablePixie(pixie, True)
        PixieCache.pixiesCount += 1

    def __attachTTL(self, effectDesc, effectID, pixie):
        ttl = effectDesc[PixieNode._PIXIE_TTL]
        if pixie is not None:
            self.__node.attach(pixie)
            effectDesc[PixieNode._PIXIE_REF] = pixie
            pixie.drawOrder = self.__drawOrder
            PixieBG.enablePixie(pixie, True)
            self.__ttlCallbacks[effectID] = BigWorld.callback(ttl, partial(self.__detachTTL, effectID))
            PixieCache.pixiesCount += 1
        return

    def __detachTTL(self, effectID):
        del self.__ttlCallbacks[effectID]
        effectDesc = self.__effects[effectID]
        self.__detach(effectDesc)

    def __detach(self, effectDesc):
        pixieRef = effectDesc[PixieNode._PIXIE_REF]
        if not self.__node.isDangling:
            self.__node.detach(pixieRef)
        PixieCache.pixiesCount -= 1
        effectDesc[PixieNode._PIXIE_REF] = None
        return

    def enable(self, effectID, enable):
        effectDesc = self.__effects.get(effectID, None)
        if self.__node.isDangling or effectDesc is None:
            return False
        else:
            if effectDesc[PixieNode._PIXIE_ENABLED] != enable:
                if enable:
                    if effectDesc[PixieNode._PIXIE_TTL] > 0.0:
                        ttlCbk = self.__ttlCallbacks.get(effectID, None)
                        if ttlCbk is not None:
                            BigWorld.cancelCallback(ttlCbk)
                            self.__ttlCallbacks[effectID] = BigWorld.callback(effectDesc[PixieNode._PIXIE_TTL], partial(self.__detachTTL, effectID))
                        else:
                            PixieCache.getPixie(effectDesc[PixieNode._PIXIE_NAME], (weakref.ref(self), effectID))
                    else:
                        pixieRef = effectDesc[PixieNode._PIXIE_REF]
                        if pixieRef is None:
                            PixieCache.getPixie(effectDesc[PixieNode._PIXIE_NAME], (weakref.ref(self), effectID))
                        else:
                            self.__attach(pixieRef)
                elif effectDesc[PixieNode._PIXIE_REF] is not None and effectDesc[PixieNode._PIXIE_TTL] == 0.0:
                    self.__detach(effectDesc)
                effectDesc[PixieNode._PIXIE_ENABLED] = enable
            return

    def correctWater(self, waterShiftRel):
        if self.__waterY:
            self.__node.local.translation = waterShiftRel + self.__nodeDefaultLocalTranslation

    def onLoadedCallback(self, pixie, effectID, clone):
        if self.__node.isDangling:
            return False
        effectDesc = self.__effects[effectID]
        prevPixie = effectDesc[PixieNode._PIXIE_REF]
        if prevPixie is not None:
            self.__detach(effectDesc)
        if effectDesc[PixieNode._PIXIE_TTL] > 0.0:
            ttlCbk = self.__ttlCallbacks.get(effectID, None)
            if ttlCbk is not None:
                BigWorld.cancelCallback(ttlCbk)
            if clone:
                pixie = pixie.clone()
            self.__attachTTL(effectDesc, effectID, pixie)
            return True
        elif effectDesc[PixieNode._PIXIE_ENABLED]:
            if clone:
                pixie = pixie.clone()
            effectDesc[PixieNode._PIXIE_REF] = pixie
            self.__attach(pixie)
            return True
        else:
            return False


class PixieCache(object):
    pixieCache = dict()
    refCount = 0
    pixiesCount = 0

    @staticmethod
    def getPixie(name, callbackData):
        pixieInfo = PixieCache.pixieCache.get(name, [None, set()])
        cbksSize = len(pixieInfo[1])
        pixieInfo[1].add(callbackData)
        if cbksSize == 0:
            pixieInfo[0] = PixieBG(name, PixieCache.onPixieLoaded)
            PixieCache.pixieCache[name] = pixieInfo
        return

    @staticmethod
    def incref():
        PixieCache.refCount += 1

    @staticmethod
    def decref():
        PixieCache.refCount -= 1
        if PixieCache.refCount == 0:
            PixieCache.pixieCache.clear()

    @staticmethod
    def onPixieLoaded(pixieBG):
        pixieInfo = PixieCache.pixieCache.get(pixieBG.name, None)
        if pixieInfo is not None:
            callbacks = pixieInfo[1]
            origPixieAccepted = False
            for callback in callbacks:
                node = callback[0]()
                if node is not None:
                    if node.onLoadedCallback(pixieBG.pixie, callback[1], origPixieAccepted):
                        origPixieAccepted = True

            if not origPixieAccepted:
                pixieBG.pixie.removeAllSystems()
            PixieCache.pixieCache[pixieBG.name] = [None, set()]
        else:
            pixieBG.pixie.removeAllSystems()
        return


class SelectorDescFactory:

    @staticmethod
    def initFactory(section):
        SelectorDescFactory.readConstants(section)
        SelectorDescFactory.readNodes(section)
        SelectorDescFactory.readTemplates(section)

    @staticmethod
    def releseFactory():
        global gTemplates
        global gNodes
        global gConstantGroup
        gTemplates = dict()
        gNodes = dict()
        gConstantGroup = dict()

    @staticmethod
    def readTemplates(dataSection):
        global gTemplates
        gTemplates = dict()
        try:
            section = dataSection['templates']
            for template in section.items():
                templateName = template[1].readString('name', '')
                selectorTemplate = SelectorDescFactory.create(template[1]['selector'])
                if selectorTemplate is not None and templateName != '':
                    gTemplates[templateName] = selectorTemplate

        except Exception:
            LOG_CURRENT_EXCEPTION()

        return

    @staticmethod
    def readNodes(dataSection):
        global gNodes
        gNodes = dict()
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
    def readConstants(dataSection):
        global gConstantGroup
        gConstantGroup = dict()
        try:
            section = dataSection['constants']
            for group in section.items():
                groupName = group[1].readString('name', '')
                groupValues = dict()
                for constDesc in group[1].items():
                    name = constDesc[1].readString('name', '').strip()
                    if len(name) > 0:
                        value = constDesc[1].readString('value', '').strip()
                        try:
                            value = float(value)
                        except:
                            pass

                        groupValues[name] = value

                gConstantGroup[groupName] = groupValues

        except Exception:
            LOG_CURRENT_EXCEPTION()

    @staticmethod
    def create(selectorDesc, effects=None):
        selectorType = selectorDesc.readString('type', '')
        selector = None
        if selectorType == 'discrete':
            selector = DiscreteSelectorDesc()
        elif selectorType == 'range':
            selector = RangeSelectorDesc()
        elif selectorType == 'effect':
            selector = EffectSelectorDesc()
        elif selectorType == 'matkind':
            selector = MatkindSelectorDesc()
        elif selectorType == 'union':
            selector = UnionSelectorDesc()
        elif selectorType == 'template':
            templateName = selectorDesc.readString('name')
            templateArgs = selectorDesc.readString('parameters')
            constantGroupName = selectorDesc.readString('constantsGroup')
            if templateName is not None:
                template = gTemplates.get(templateName, None)
                if template is not None:
                    selector = copy.deepcopy(template)
                    templateArgsDict = dict()
                    if len(templateArgs) > 0:
                        templateArgsList = templateArgs.split(';')
                        for argument in templateArgsList:
                            argumetSplit = argument.split(':')
                            if len(argumetSplit) < 2:
                                continue
                            name = argumetSplit[0].strip()
                            value = argumetSplit[1].strip()
                            try:
                                value = float(value)
                            except:
                                pass

                            templateArgsDict[name] = value

                    constantGroupDict = gConstantGroup.get(constantGroupName, None)
                    if constantGroupDict is not None:
                        templateArgsDict.update(constantGroupDict)
                    selector.fillTemplate(templateArgsDict, effects)
                    return selector
        if selector is not None:
            selector.read(selectorDesc, effects)
        return selector


class SelectorDesc(object):

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

    def getActiveEffects(self, effects, args=None):
        pass


class DiscreteSelectorDesc(SelectorDesc):

    @property
    def selectors(self):
        return self._selectors

    def __init__(self):
        super(DiscreteSelectorDesc, self).__init__()
        self._selectors = dict()

    def read(self, dataSection, effects):
        super(DiscreteSelectorDesc, self).read(dataSection, effects)
        self._variable = dataSection['variable'].asString.strip()
        for selectorDesc in dataSection.items():
            if selectorDesc[0] == 'selector':
                value = selectorDesc[1]['key'].asString.strip()
                try:
                    value = float(value)
                except:
                    pass

                self._selectors[value] = SelectorDescFactory.create(selectorDesc[1], effects)

    def fillTemplate(self, args, effects):
        self._variable = args.get(self._variable, self._variable)
        newSelectors = dict()
        for key, selector in self._selectors.iteritems():
            selector.fillTemplate(args, effects)
            newKey = args.get(key, key)
            newSelectors[newKey] = selector

        self._selectors = newSelectors

    def getActiveEffects(self, effects, args=None):
        keyValue = args[self._variable]
        if keyValue is None:
            return
        else:
            value = self._selectors.get(keyValue, None)
            if value is not None:
                value.getActiveEffects(effects, args)
            return


class MatkindSelectorDesc(DiscreteSelectorDesc):

    def __init__(self):
        super(MatkindSelectorDesc, self).__init__()

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
                except:
                    pass

                keys.append(value)
                values.append(SelectorDescFactory.create(selectorDesc[1], effects))

        self.__keys = tuple(keys)
        self._selectors = tuple(values)

    def fillTemplate(self, args, effects):
        self._variable = args.get(self._variable, self._variable)
        newKeys = []
        for i in xrange(len(self.__keys)):
            newKeys.append(args.get(self.__keys[i], self.__keys[i]))
            self._selectors[i].fillTemplate(args, effects)

        self.__keys = tuple(newKeys)

    def getActiveEffects(self, effects, args=None):
        keyValue = args[self._variable]
        if keyValue is None:
            return
        else:
            idx = -1
            for leftBound in self.__keys:
                if keyValue < leftBound:
                    break
                idx += 1

            return self._selectors[idx].getActiveEffects(effects, args) if idx > -1 and idx < len(self._selectors) else None


class UnionSelectorDesc(SelectorDesc):

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

    def getActiveEffects(self, effects, args=None):
        isPc = args['isPC']
        for selector in self._selectors:
            if selector._isPC is None:
                selector.getActiveEffects(effects, args)
            if selector._isPC == isPc:
                selector.getActiveEffects(effects, args)

        return


class EffectSelectorDesc(SelectorDesc):

    def __init__(self):
        super(EffectSelectorDesc, self).__init__()
        self.__hardPoint = None
        self._id = None
        self.__ttl = 0.0
        return

    def read(self, dataSection, effects):
        self._variable = dataSection['name'].asString.strip()
        self.__hardPoint = dataSection['effectHP']
        ttlSection = dataSection['ttl']
        if self.__hardPoint is not None:
            self.__hardPoint = self.__hardPoint.asString.strip()
        if ttlSection is not None:
            ttlSection = ttlSection.asString.strip()
            try:
                self.__ttl = float(ttlSection)
            except:
                pass

        self.__makeId(effects)
        return

    def fillTemplate(self, args, effects):
        self._variable = args.get(self._variable, self._variable)
        self.__ttl = args.get(self.__ttl, self.__ttl)
        fileDesc = args.get('_fileDescriptor', '')
        if len(fileDesc) > 0:
            self._variable = self._variable.format(fileDesc)
        if self.__hardPoint is not None:
            self.__hardPoint = args.get(self.__hardPoint, self.__hardPoint)
            self.__makeIdWithHP(effects)
        else:
            self.__makeId(effects)
        return

    def getActiveEffects(self, effects, args=None):
        effects.add(self._id)

    def __makeId(self, effects):
        if effects is not None:
            effectID = effects.get(self._variable, None)
            if effectID is None:
                effectID = len(effects)
                effects[self._variable] = (effectID, self.__ttl)
            else:
                effectID = effectID[0]
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
                nodeEffects[4][self._variable] = (effectID, self.__ttl)
            else:
                effectID = effectID[0]
            self._id = (self._id, effectID)
        return


class EffectDescriptorBase(object):

    def __init__(self):
        self._selectorDesc = None
        return

    def getActiveEffects(self, args, effectIDs):
        pass


class CustomEffectsDescriptor(EffectDescriptorBase):

    @staticmethod
    def getDescriptor(dataSection, customDescriptors, xmlCtx, name):
        effectName = _xml.readNonEmptyString(xmlCtx, dataSection, name)
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
        if self._selectorDesc is not None:
            return MainCustomSelector(self, args)
        else:
            return
            return

    def getActiveEffects(self, args, effectIDs):
        return self._selectorDesc.getActiveEffects(args, effectIDs) if self._selectorDesc is not None else None


class ExhaustEffectDescriptor(EffectDescriptorBase):

    def __init__(self, dataSection, xmlCtx, customDescriptor, name):
        super(ExhaustEffectDescriptor, self).__init__()
        self._selectorDesc = customDescriptor
        self.nodes = _xml.readNonEmptyString(xmlCtx, dataSection, name).split()

    def create(self, args):
        if self._selectorDesc is not None:
            return ExhaustMainSelector(self._selectorDesc, args, self.nodes)
        else:
            return
            return

    def getActiveEffects(self, args, effectIDs):
        return self._selectorDesc.getActiveEffects(args, effectIDs) if self._selectorDesc is not None else None


class EffectSettings:
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
        self._enabled = False
        for effect in self._activeEffectId:
            self.enable(effect, False)

        self._activeEffectId = set()

    def update(self, args):
        if not self._enabled:
            return
        activeEffects = set()
        self._effectSelector.getActiveEffects(activeEffects, args)
        disableEffects = self._activeEffectId.difference(activeEffects)
        for effect in disableEffects:
            self.enable(effect, False)

        enableEffects = activeEffects.difference(self._activeEffectId)
        for effect in enableEffects:
            self.enable(effect, True)

        self._activeEffectId = activeEffects


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
                model.node(nodeName, Math.Matrix(node.localMatrix))
                drawOrderBase = args.get('drawOrderBase', 0)
                self._effectNodes[nodeDesc[0]] = PixieNode(node, nodeDesc[2], drawOrderBase + nodeDesc[3], nodeDesc[4])
            except:
                LOG_ERROR('Node %s is not found' % nodeName)
                continue

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
        self._effectNodes = dict()
        for nodeName in nodes:
            model = args['hull']['model']
            try:
                node = model.node(nodeName)
                model.node(nodeName, Math.Matrix(node.localMatrix))
                drawOrderBase = args.get('drawOrderBase', 0)
                self._effectNodes[nodeName] = PixieNode(node, False, drawOrderBase, self._effectSelector.effects)
            except:
                LOG_ERROR('Node %s is not found' % nodeName)
                continue

    def enable(self, effectID, enable):
        for node in self._effectNodes.values():
            node.enable(effectID, enable)
