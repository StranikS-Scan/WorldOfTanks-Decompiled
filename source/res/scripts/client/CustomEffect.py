# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/CustomEffect.py
import BigWorld
import copy
import Math
import material_kinds
import Pixie
from items import _xml
from functools import partial
from debug_utils import *
import weakref
gTemplates = None
gNodes = None
gConstantGroup = None
_CACHED_PIXIE_MODEL = False

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


def enablePixie(pixie, turnOn):
    multiplier = 1.0 if turnOn else 0.0
    for i in xrange(pixie.nSystems()):
        try:
            source = pixie.system(i).action(16)
            source.MultRate(multiplier)
        except:
            LOG_CURRENT_EXCEPTION()


class PixieNode(object):
    _PIXIE_NAME = 0
    _PIXIE_ENABLED = 1
    _PIXIE_REF = 2
    _PIXIE_TTL = 3

    def __init__(self, node, waterY, drawOrder, effects):
        self.__node = node
        self.__drawOrder = drawOrder
        self.__waterY = waterY
        self.__effects = [None] * len(effects)
        self.__ttlCallbacks = [None] * len(effects)
        for effectName, effectDesc in effects.iteritems():
            self.__effects[effectDesc[0]] = [effectName,
             False,
             None,
             effectDesc[1]]

        return

    def destroy(self):
        for cbkId in self.__ttlCallbacks:
            if cbkId is not None:
                BigWorld.cancelCallback(cbkId)

        for effectDesc in self.__effects:
            pixieRef = effectDesc[PixieNode._PIXIE_REF]
            if pixieRef is not None:
                self.__detach(effectDesc)

        self.__effects = None
        self.__ttlCallbacks = None
        return

    def __attach(self, pixie):
        self.__node.attach(pixie)
        pixie.drawOrder = self.__drawOrder
        enablePixie(pixie, True)

    def __attachTTL(self, effectID, pixie, ttl):
        effectDesc = self.__effects[effectID]
        effectDesc[PixieNode._PIXIE_REF] = pixie
        self.__node.attach(pixie)
        pixie.drawOrder = self.__drawOrder
        enablePixie(pixie, True)
        self.__ttlCallbacks[effectID] = BigWorld.callback(ttl, partial(self.__detachTTL, effectID))

    def __detachTTL(self, effectID):
        self.__ttlCallbacks[effectID] = None
        effectDesc = self.__effects[effectID]
        self.__detach(effectDesc)
        return

    def __detach(self, effectDesc):
        pixieRef = effectDesc[PixieNode._PIXIE_REF]
        effectDesc[PixieNode._PIXIE_REF] = None
        self.__node.detach(pixieRef)
        enablePixie(pixieRef, False)
        pixieRef.removeAllSystems()
        if _CACHED_PIXIE_MODEL:
            PixieCache.retPixie(effectDesc[PixieNode._PIXIE_NAME], pixieRef)
        return

    def enable(self, effectID, enable):
        effectDesc = self.__effects[effectID]
        if effectDesc[PixieNode._PIXIE_ENABLED] != enable:
            if enable:
                if effectDesc[PixieNode._PIXIE_TTL] > 0.0:
                    if self.__ttlCallbacks[effectID] is not None:
                        BigWorld.cancelCallback(self.__ttlCallbacks[effectID])
                        self.__ttlCallbacks[effectID] = BigWorld.callback(effectDesc[PixieNode._PIXIE_TTL], partial(self.__detachTTL, effectID))
                    else:
                        pixieRef = PixieCache.getPixie(effectDesc[PixieNode._PIXIE_NAME], (weakref.ref(self), effectID))
                        if pixieRef is not None:
                            self.__attachTTL(effectID, pixieRef, effectDesc[PixieNode._PIXIE_TTL])
                else:
                    pixieRef = effectDesc[PixieNode._PIXIE_REF]
                    if pixieRef is None:
                        pixieRef = PixieCache.getPixie(effectDesc[PixieNode._PIXIE_NAME], (weakref.ref(self), effectID))
                    if pixieRef is not None:
                        effectDesc[PixieNode._PIXIE_REF] = pixieRef
                        self.__attach(pixieRef)
            elif effectDesc[PixieNode._PIXIE_REF] is not None and effectDesc[PixieNode._PIXIE_TTL] == 0.0:
                self.__detach(effectDesc)
            effectDesc[PixieNode._PIXIE_ENABLED] = enable
        return

    def correctWater(self, position, waterHeight):
        if self.__waterY:
            if waterHeight != 0.0:
                toCenterShift = position.y - (Math.Matrix(self.__node).translation.y - self.__node.local.translation.y)
                self.__node.local.translation = Math.Vector3(0.0, waterHeight + toCenterShift, 0.0)
            else:
                self.__node.local.translation = Math.Vector3(0.0, 0.0, 0.0)

    def onLoadedCallback(self, pixie, effectID):
        effectDesc = self.__effects[effectID]
        if effectDesc[PixieNode._PIXIE_TTL] > 0.0:
            if self.__ttlCallbacks[effectID] is None:
                self.__attachTTL(effectID, pixie, effectDesc[PixieNode._PIXIE_TTL])
                return True
            else:
                return False
        if effectDesc[PixieNode._PIXIE_ENABLED]:
            effectDesc[PixieNode._PIXIE_REF] = pixie
            self.__attach(pixie)
            return False
        else:
            return True


class PixieCache(object):
    pixieCache = dict()
    refCount = 0
    pixiesCount = 0

    @staticmethod
    def getPixie(name, callbackData):
        pixieInfo = PixieCache.pixieCache.get(name, (None, set()))
        if pixieInfo[0] is None:
            cbksSize = len(pixieInfo[1])
            pixieInfo[1].add(callbackData)
            if cbksSize == 0:
                Pixie.createBG(name, partial(PixieCache.onPixieLoaded, name))
                PixieCache.pixieCache[name] = pixieInfo
            return
        else:
            if _CACHED_PIXIE_MODEL:
                if len(pixieInfo) == 1:
                    newPixie = pixieInfo[0].clone()
                else:
                    newPixie = pixieInfo.pop()
            else:
                newPixie = pixieInfo[0].clone()
            return newPixie
            return

    @staticmethod
    def retPixie(name, pixie):
        if _CACHED_PIXIE_MODEL:
            if pixie is not None:
                pixieInfo = PixieCache.pixieCache[name]
                pixieInfo.append(pixie)
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
    def onPixieLoaded(name, pixie):
        if pixie is None:
            LOG_ERROR("Can't create pixie '%s'." % name)
            return
        else:
            pixieInfo = PixieCache.pixieCache.get(name, None)
            if pixieInfo is not None:
                callbacks = pixieInfo[1]
                pixieList = [pixie]
                if _CACHED_PIXIE_MODEL:
                    for callback in callbacks:
                        newPixie = pixie.clone()
                        if callback(newPixie):
                            pixieList.append(newPixie)

                else:
                    for callback in callbacks:
                        node = callback[0]()
                        if node is not None:
                            node.onLoadedCallback(pixie.clone(), callback[1])

                PixieCache.pixieCache[name] = pixieList
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

    @property
    def variable(self):
        return self._variable

    def __init__(self):
        self._variable = None
        return

    def read(self, dataSection, effects):
        pass

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

        self._selectors = RangeTable(keys, values)

    def fillTemplate(self, args, effects):
        self._variable = args.get(self._variable, self._variable)
        for i in xrange(len(self._selectors.keys)):
            self._selectors.keys[i] = args.get(self._selectors.keys[i], self._selectors.keys[i])
            self._selectors.values[i].fillTemplate(args, effects)

    def getActiveEffects(self, effects, args=None):
        keyValue = args[self._variable]
        if keyValue is None:
            return
        else:
            selector = self._selectors.lookup(keyValue)
            if selector is not None:
                selector.getActiveEffects(effects, args)
            return


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
        for selector in self._selectors:
            selector.getActiveEffects(effects, args)


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


class MainSelectorBase(object):

    @property
    def effectNodes(self):
        return self._effectNodes

    def __init__(self, selectorDesc, args):
        self._activeEffectId = set()
        self._effectSelector = selectorDesc
        self._effectNodes = None
        self._enabled = True
        return

    def destroy(self):
        if self._effectNodes is not None:
            for node in self._effectNodes:
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
        self._effectNodes = [None] * len(self._effectSelector.effects)
        for nodeName, nodeDesc in effects.iteritems():
            modelName = nodeDesc[1]
            identity = Math.Matrix()
            identity.setIdentity()
            model = args[modelName]['model']
            try:
                node = model.node(nodeName, identity)
                drawOrderBase = args.get('drawOrderBase', 0)
                self._effectNodes[nodeDesc[0]] = PixieNode(node, nodeDesc[2], drawOrderBase + nodeDesc[3], nodeDesc[4])
            except:
                LOG_ERROR('Node %s is not found' % nodeName)
                continue

        return

    def enable(self, effectID, enable):
        node = self._effectNodes[effectID[0]]
        if node is not None:
            node.enable(effectID[1], enable)
        return


class ExhaustMainSelector(MainSelectorBase):

    def __init__(self, selectorDesc, args, nodes):
        super(ExhaustMainSelector, self).__init__(selectorDesc, args)
        self.__createEffects(selectorDesc.effects, args, nodes)

    def settingsFlags(self):
        return EffectSettings.SETTINGS_NO

    def __createEffects(self, effects, args, nodes):
        self._effectNodes = []
        for nodeName in nodes:
            identity = Math.Matrix()
            identity.setIdentity()
            model = args['hull']['model']
            try:
                node = model.node(nodeName, identity)
                drawOrderBase = args.get('drawOrderBase', 0)
                self._effectNodes.append(PixieNode(node, False, drawOrderBase, self._effectSelector.effects))
            except:
                LOG_ERROR('Node %s is not found' % nodeName)
                continue

    def enable(self, effectID, enable):
        for node in self._effectNodes:
            node.enable(effectID, enable)
