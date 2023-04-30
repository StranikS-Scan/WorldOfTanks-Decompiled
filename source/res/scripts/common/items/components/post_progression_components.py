# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/post_progression_components.py
import ResMgr
from constants import IS_CLIENT, IS_WEB, TTC_TOOLTIP_SECTIONS
from items import _xml
from items.attributes_helpers import readModifiers
from items.artefacts_helpers import VehicleFilter, readKpi
from typing import Dict, Optional, Tuple, List, Union, Set
from post_progression_common import ACTION_TYPES, FEATURES_NAMES, PAIR_TYPES, parseActionCompDescr, ID_THRESHOLD, POST_PROGRESSION_UNLOCK_MODIFICATIONS_PRICES, POST_PROGRESSION_BUY_MODIFICATIONS_PRICES, POST_PROGRESSION_UNLOCK_AND_BUY_MODIFICATIONS_PRICES, ALLOWED_CURRENCIES_FOR_TREE_STEP, ALLOWED_CURRENCIES_FOR_BUY_MODIFICATION_STEP
from soft_exception import SoftException

def getFeatures(actionCDs, vppCache):
    result = set()
    for actionCD in actionCDs:
        actionType, itemId, subId = parseActionCompDescr(actionCD)
        if actionType == ACTION_TYPES.FEATURE:
            featureName = vppCache.features[itemId].name
            result.add(featureName)

    return result


def getActiveModifications(actionCDs, vppCache):
    result = []
    for actionCD in actionCDs:
        actionType, itemID, subID = parseActionCompDescr(actionCD)
        if actionType == ACTION_TYPES.MODIFICATION:
            result.append(itemID)
        if actionType == ACTION_TYPES.PAIR_MODIFICATION:
            if subID == PAIR_TYPES.FIRST:
                result.append(vppCache.pairs[itemID].first[0])
            elif subID == PAIR_TYPES.SECOND:
                result.append(vppCache.pairs[itemID].second[0])

    return result


class SimpleItem(object):
    __slots__ = ('id',)

    def __init__(self):
        self.id = None
        return

    def readFromXML(self, xmlCtx, section, *args):
        xmlCtx = (xmlCtx, section.name)
        self.id = _xml.readInt(xmlCtx, section, 'id', 1)


class ActionItem(SimpleItem):
    __slots__ = ('name', 'actionType', 'locName', 'imgName', 'tooltipSection')

    def __init__(self):
        super(ActionItem, self).__init__()
        self.name = None
        self.imgName = None
        self.locName = None
        self.actionType = None
        return

    def readFromXML(self, xmlCtx, section, *args):
        super(ActionItem, self).readFromXML(xmlCtx, section, *args)
        if self.id >= ID_THRESHOLD:
            _xml.raiseWrongXml(xmlCtx, 'id', 'id: {} must be less than {}'.format(self.id, ID_THRESHOLD))
        self.name = section.name
        if IS_CLIENT or IS_WEB:
            self.imgName = _xml.readStringWithDefaultValue(xmlCtx, section, 'imgName', self.name)
            self.locName = _xml.readStringWithDefaultValue(xmlCtx, section, 'locName', self.name)
            self.tooltipSection = _xml.readStringWithDefaultValue(xmlCtx, section, 'tooltipSection', TTC_TOOLTIP_SECTIONS.EQUIPMENT)


class Modification(ActionItem):
    __slots__ = ('kpi', 'modifiers')

    def __init__(self):
        super(Modification, self).__init__()
        self.actionType = ACTION_TYPES.MODIFICATION
        self.modifiers = None
        self.kpi = []
        return

    def readFromXML(self, xmlCtx, section, *args):
        super(Modification, self).readFromXML(xmlCtx, section, *args)
        xmlCtx = (xmlCtx, section.name)
        self.modifiers = readModifiers(xmlCtx, section['modifiers'])
        if IS_CLIENT and section.has_key('kpi'):
            self.kpi = readKpi(xmlCtx, section['kpi'])


class PairModification(ActionItem):
    __slots__ = ('first', 'second')

    def __init__(self):
        super(PairModification, self).__init__()
        self.actionType = ACTION_TYPES.PAIR_MODIFICATION
        self.first = None
        self.second = None
        return

    def readFromXML(self, xmlCtx, section, *args):
        super(PairModification, self).readFromXML(xmlCtx, section, *args)
        xmlCtx = (xmlCtx, section.name)
        modifications = args[0]
        self.first = self._readModificationID(xmlCtx, section['first'], modifications)
        self.second = self._readModificationID(xmlCtx, section['second'], modifications)

    @staticmethod
    def _readModificationID(xmlCtx, section, modificationIDs):
        xmlCtx = (xmlCtx, section.name)
        name = _xml.readString(xmlCtx, section, 'name')
        priceTag = _xml.readString(xmlCtx, section, 'price')
        modificationID = modificationIDs.get(name)
        if modificationID is None:
            _xml.raiseWrongXml(xmlCtx, name, 'Unknown modification')
        return (modificationID, priceTag)


class ProgressionFeature(ActionItem):
    __slots__ = ()

    def __init__(self):
        super(ProgressionFeature, self).__init__()
        self.actionType = ACTION_TYPES.FEATURE

    def readFromXML(self, xmlCtx, section, *args):
        super(ProgressionFeature, self).readFromXML(xmlCtx, section, *args)
        if self.name not in FEATURES_NAMES:
            _xml.raiseWrongXml(xmlCtx, section.name, 'Unknown feature name')


class TreeStep(SimpleItem):
    __slots__ = ('priceTag', 'action', 'unlocks', 'requiredUnlocks', 'vehicleFilter', 'level')

    def __init__(self):
        super(TreeStep, self).__init__()
        self.priceTag = None
        self.action = None
        self.unlocks = None
        self.requiredUnlocks = tuple()
        self.vehicleFilter = None
        self.level = None
        return

    def readFromXML(self, xmlCtx, section, *args):
        super(TreeStep, self).readFromXML(xmlCtx, section, *args)
        xmlCtx = (xmlCtx, section.name)
        self.priceTag = _xml.readString(xmlCtx, section, 'price')
        self.action = self._readAction(xmlCtx, section['action'], args[0])
        self.unlocks = _xml.readTupleOfInts(xmlCtx, section, 'unlocks') if section.has_key('unlocks') else tuple()
        self.level = _xml.readInt(xmlCtx, section, 'level')
        if section.has_key('vehicleFilter'):
            self.vehicleFilter = VehicleFilter.readVehicleFilter((xmlCtx, 'vehicleFilter'), section['vehicleFilter'])
        else:
            self.vehicleFilter = None
        return

    def addRequiredUnlock(self, stepID):
        self.requiredUnlocks = self.requiredUnlocks + (stepID,)

    @staticmethod
    def _readAction(xmlCtx, section, actionResolvers):
        if section is None:
            _xml.raiseWrongXml(xmlCtx, None, 'Action not found')
        xmlCtx = (xmlCtx, section.name)
        actionType = _xml.readString(xmlCtx, section, 'type')
        actionValue = _xml.readString(xmlCtx, section, 'value')
        resolver = actionResolvers.get(actionType)
        if resolver is None:
            _xml.raiseWrongXml(xmlCtx, actionType, 'Unknown action specified')
        typeID, valueID = resolver(actionValue)
        if valueID is None:
            _xml.raiseWrongXml(xmlCtx, actionValue, 'Unknown value for specified action type')
        return (typeID, valueID)


class ProgressionTree(SimpleItem):
    __slots__ = ('steps', 'rootStep')

    def __init__(self):
        super(ProgressionTree, self).__init__()
        self.steps = None
        self.rootStep = None
        return

    def readFromXML(self, xmlCtx, section, *args):
        super(ProgressionTree, self).readFromXML(xmlCtx, section, *args)
        xmlCtx = (xmlCtx, section.name)
        if not section.has_key('steps'):
            _xml.raiseWrongXml(xmlCtx, None, 'Steps not found')
        features, modifications, pairModifications = args
        _ACTION_RESOLVERS = {'modification': lambda x: (ACTION_TYPES.MODIFICATION, modifications.get(x)),
         'pair_modification': lambda x: (ACTION_TYPES.PAIR_MODIFICATION, pairModifications.get(x)),
         'feature': lambda x: (ACTION_TYPES.FEATURE, features.get(x))}
        steps = {}
        for name, data in section['steps'].items():
            if name != 'step':
                _xml.raiseWrongXml(xmlCtx, name, 'Unexpected subsection')
            step = TreeStep()
            step.readFromXML(xmlCtx, data, _ACTION_RESOLVERS)
            steps[step.id] = step

        for stepID, step in steps.iteritems():
            for unlockID in step.unlocks:
                steps[unlockID].addRequiredUnlock(stepID)

        self.steps = steps
        self.rootStep = _xml.readInt(xmlCtx, section, 'rootStep')
        if self.rootStep not in self.steps or steps[self.rootStep].requiredUnlocks:
            _xml.raiseWrongXml(xmlCtx, None, 'Invalid root step id {}'.format(self.rootStep))
        self._validateLevels(xmlCtx)
        return

    def _validateLevels(self, xmlCtx):
        for stepID, step in self.steps.iteritems():
            for unlockID in step.unlocks:
                if self.steps[unlockID].level < step.level:
                    _xml.raiseWrongXml(xmlCtx, None, 'Invalid step level for step: {}'.format(stepID))

        return


class PostProgressionCache(object):
    __slots__ = ('_features', '_featureIDs', '_modifications', '_modificationIDs', '_pairs', '_pairIDs', '_trees', '_treeIDs', '_prices', 'actionToStorage')

    def __init__(self, featuresXML, modificationsXML, pairsXML, treesXML, pricesXML):
        self._features, self._featureIDs = self._readItems(featuresXML, ProgressionFeature)
        self._modifications, self._modificationIDs = self._readItems(modificationsXML, Modification)
        self._pairs, self._pairIDs = self._readItems(pairsXML, PairModification, self._modificationIDs)
        self._trees, self._treeIDs = self._readItems(treesXML, ProgressionTree, self.featureIDs, self.modificationIDs, self.pairIDs)
        self._prices = self._readPrices(pricesXML)
        self.actionToStorage = {ACTION_TYPES.FEATURE: self._features,
         ACTION_TYPES.MODIFICATION: self._modifications,
         ACTION_TYPES.PAIR_MODIFICATION: self._pairs}

    @property
    def features(self):
        return self._features

    @property
    def featureIDs(self):
        return self._featureIDs

    @property
    def modifications(self):
        return self._modifications

    @property
    def modificationIDs(self):
        return self._modificationIDs

    @property
    def pairs(self):
        return self._pairs

    @property
    def pairIDs(self):
        return self._pairIDs

    @property
    def trees(self):
        return self._trees

    @property
    def treeIDs(self):
        return self._treeIDs

    @property
    def prices(self):
        return self._prices

    def getAction(self, actionType, actionID):
        return self.actionToStorage[actionType][actionID]

    def getChildActions(self, parent):
        return [ (self.modifications[modificationID], priceTag) for modificationID, priceTag in (parent.first, parent.second) ]

    def getModificationByName(self, name):
        return self._modifications[self._modificationIDs[name]] if name in self._modificationIDs else None

    def _readItems(self, xmlPath, classObj, *args):
        xmlCtx = (None, xmlPath)
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'Unable to open or read')
        ids = dict()
        names = dict()
        for name, data in section.items():
            item = classObj()
            item.readFromXML(xmlCtx, data, *args)
            if item.id in ids:
                _xml.raiseWrongXml(xmlCtx, name, 'Duplicate item id')
            if name in names:
                _xml.raiseWrongXml(xmlCtx, name, 'Duplicate item name')
            names[name] = item.id
            ids[item.id] = item

        ResMgr.purge(xmlPath)
        return (ids, names)

    @staticmethod
    def _readPrices(xmlPath):
        xmlCtx = (None, xmlPath)
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'Unable to open or read')
        prices = dict()
        for name, data in section.items():
            if name not in POST_PROGRESSION_UNLOCK_AND_BUY_MODIFICATIONS_PRICES:
                _xml.raiseWrongXml(xmlCtx, name, 'Incorrect price tag <%s>' % name)
            ctx = (xmlCtx, name)
            prices[name] = dict()
            for sname, _ in data.items():
                _, level = str(sname).split('_', 1)
                prices[name][int(level)] = _xml.readPostProgressionPrice(ctx, data, sname)

            if name in POST_PROGRESSION_UNLOCK_MODIFICATIONS_PRICES:
                for _, value in prices[name].iteritems():
                    if not ALLOWED_CURRENCIES_FOR_TREE_STEP.issuperset(value.keys()):
                        raise SoftException('Wrong currency for section: {}, path: {}'.format(name, xmlPath))

            if name in POST_PROGRESSION_BUY_MODIFICATIONS_PRICES:
                for _, value in prices[name].iteritems():
                    if not ALLOWED_CURRENCIES_FOR_BUY_MODIFICATION_STEP.issuperset(value.keys()):
                        raise SoftException('Wrong currency for section: {}, path: {}'.format(name, xmlPath))

        return prices
