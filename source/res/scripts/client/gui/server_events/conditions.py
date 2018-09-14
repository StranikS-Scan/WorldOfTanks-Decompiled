# Embedded file name: scripts/client/gui/server_events/conditions.py
import weakref
import operator
from abc import ABCMeta, abstractmethod
import BigWorld
import constants
import nations
import account_helpers
from debug_utils import LOG_WARNING, LOG_DEBUG
from helpers import i18n, int2roman
from items import vehicles
from gui import makeHtmlString
from gui.shared import g_itemsCache, REQ_CRITERIA
from gui.shared.utils import CONST_CONTAINER
from gui.server_events import formatters
_AVAILABLE_BONUS_TYPES_LABELS = {constants.ARENA_BONUS_TYPE.COMPANY: 'company',
 constants.ARENA_BONUS_TYPE.CYBERSPORT: 'team7x7'}
_RELATIONS = formatters.RELATIONS
_RELATIONS_SCHEME = formatters.RELATIONS_SCHEME

def _getArenaBonusType(preBattleCond):
    if preBattleCond is not None:
        squadNode = preBattleCond.getConditions().find('isSquad')
        if squadNode is not None and squadNode.getValue():
            return 'squad'
        bonusTypeNode = preBattleCond.getConditions().find('bonusTypes')
        if bonusTypeNode is not None:
            bonusTypes = list(bonusTypeNode.getValue())
            if len(bonusTypes) == 1 and bonusTypes[0] in _AVAILABLE_BONUS_TYPES_LABELS:
                return _AVAILABLE_BONUS_TYPES_LABELS[bonusTypes[0]]
    return 'formation'


class GROUP_TYPE(CONST_CONTAINER):
    OR = 'or'
    AND = 'and'


_SORT_ORDER = ('igrType', 'premiumAccount', 'token', 'inClan', 'GR', 'accountDossier', 'vehiclesUnlocked', 'vehiclesOwned', 'hasReceivedMultipliedXP', 'vehicleDossier', 'vehicleDescr', 'bonusTypes', 'isSquad', 'camouflageKind', 'geometryNames', 'win', 'isAlive', 'achievements', 'results', 'unitResults', 'vehicleKills', 'clanKills', 'cumulative', 'vehicleKillsCumulative')
_SORT_ORDER_INDICES = dict(((name, idx) for idx, name in enumerate(_SORT_ORDER)))

def _handleRelation(relation, source, toCompare):
    if relation == _RELATIONS.EQ:
        return source == toCompare
    if relation == _RELATIONS.GT:
        return source > toCompare
    if relation == _RELATIONS.GTQ:
        return source >= toCompare
    if relation == _RELATIONS.LS:
        return source < toCompare
    if relation == _RELATIONS.LSQ:
        return source <= toCompare
    LOG_WARNING('Unknown kind of values relation', relation, source, toCompare)
    return False


def _findRelation(condDataKeys):
    res = set(_RELATIONS.ALL()) & set(condDataKeys)
    if len(res):
        return res.pop()
    else:
        return None


def _getNodeValue(node, key, default = None):
    if key in node:
        dNode = dict(node[key])
        if 'value' in dNode:
            return dNode['value']
    return default


def _prepareVehData(vehsList, predicate = None):
    predicate = predicate or (lambda *args: True)
    return map(lambda v: (v, (not v.isInInventory or predicate(v), None, None)), vehsList)


class _Negatable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def negate(self):
        pass


class _Updatable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def update(self, other, groupType):
        pass


class _AvailabilityCheckable(object):
    __metaclass__ = ABCMeta

    def isAvailable(self, *args, **kwargs):
        return self._isAvailable(*args, **kwargs)

    def _isAvailable(self, *args, **kwargs):
        return True


class _Condition(object):

    def __init__(self, name, data, uniqueName):
        super(_Condition, self).__init__()
        self._name = name
        self._data = data
        self._uniqueName = uniqueName

    def getName(self):
        return self._name

    def getData(self):
        return self._data

    def getUniqueName(self):
        return self._uniqueName

    def clearItemsCache(self):
        pass

    def format(self, svrEvents, event = None):
        return self._format(svrEvents, event)

    def _format(self, svrEvents, event = None):
        return []


class _ConditionsGroup(_AvailabilityCheckable, _Negatable):

    def __init__(self, groupType, isNegative = False):
        super(_ConditionsGroup, self).__init__()
        self.items = []
        self.type = groupType
        self.isNegative = isNegative

    def getName(self):
        return self.type

    def isAvailable(self, *args, **kwargs):
        res = self._isAvailable(*args, **kwargs)
        if self.isNegative:
            res = not res
        return res

    def add(self, condition):
        if isinstance(condition, list) or isinstance(condition, tuple):
            for cond in condition:
                self._addNewCondition(cond)

        else:
            self._addNewCondition(condition)

    def remove(self, condition):
        self.items.remove(condition)

    def find(self, condName):
        for cond in self.items:
            if cond.getName() == condName:
                return cond

        return None

    def findAll(self, condName):
        result = []
        for cond in self.items:
            if cond.getName() == condName:
                result.append(cond)

        return result

    def negate(self):
        self.isNegative = not self.isNegative

    def isEmpty(self):
        return not len(self.items)

    def format(self, svrEvents, event = None):
        subBlocks = self._formatSubBlocks(svrEvents, event)
        if len(subBlocks) > 1:
            return [formatters.packContainer(subBlocks=subBlocks)]
        if len(subBlocks) > 0:
            return subBlocks
        return []

    def getSortedItems(self):
        return sorted(self.items, cmp=self._sortItems, key=operator.methodcaller('getName'))

    @classmethod
    def _sortItems(cls, a, b):
        if a not in _SORT_ORDER:
            return 1
        if b not in _SORT_ORDER:
            return -1
        return _SORT_ORDER_INDICES[a] - _SORT_ORDER_INDICES[b]

    def _addNewCondition(self, cond):
        if isinstance(cond, _Updatable):
            otherCond = self.find(cond.getName())
            if otherCond is None:
                self.items = [ c for c in self.items if not cond.update(c, self.type) ]
            elif otherCond.update(cond, self.type):
                cond = None
        if cond is not None:
            self.items.append(cond)
        return

    def _formatSubBlocks(self, svrEvents, event = None):
        return []

    def __repr__(self):
        return '%s<count=%d>' % (self.__class__.__name__, len(self.items))


class _Requirement(_Condition, _AvailabilityCheckable, _Negatable):

    def __repr__(self):
        return '%s<>' % self.__class__.__name__


class _VehicleRequirement(_Requirement):

    def _isAvailable(self, vehicle):
        return True


class _VehsListParser(object):

    def __init__(self):
        self.__vehsCache = None
        return

    def _clearItemsCache(self):
        self.__vehsCache = None
        return

    def _preProcessCriteria(self, criteria):
        return criteria

    def _isAnyVehicleAcceptable(self, data):
        return not len(set(data.keys()) & {'types',
         'nations',
         'levels',
         'classes'})

    def _getFilterCriteria(self, data):
        fTypes, fNations, fLevels, fClasses = self._parseFilters(data)
        if fTypes is not None:
            criteria = REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(fTypes)
        else:
            criteria = ~REQ_CRITERIA.SECRET
            if fNations is not None:
                criteria |= REQ_CRITERIA.NATIONS(fNations)
            if fLevels is not None:
                criteria |= REQ_CRITERIA.VEHICLE.LEVELS(fLevels)
            if fClasses is not None:
                criteria |= REQ_CRITERIA.VEHICLE.CLASSES(fClasses)
        return self._preProcessCriteria(criteria)

    def _getVehiclesList(self, data):
        if self.__vehsCache is None:
            self.__vehsCache = sorted(g_itemsCache.items.getVehicles(self._getFilterCriteria(data)).itervalues())
        return self.__vehsCache

    def _parseFilters(self, data):
        types, nationsList, levels, classes = (None, None, None, None)
        if 'types' in data:
            types = _getNodeValue(data, 'types')
        if 'nations' in data:
            nationsList = _getNodeValue(data, 'nations')
        if 'levels' in data:
            levels = _getNodeValue(data, 'levels')
        if 'classes' in data:
            acceptedClasses = _getNodeValue(data, 'classes')
            classes = [ name for name, index in constants.VEHICLE_CLASS_INDICES.items() if index in acceptedClasses ]
        return (types,
         nationsList,
         levels,
         classes)


class _VehsListCondition(_Condition, _VehsListParser):

    def __init__(self, name, data, path):
        super(_VehsListCondition, self).__init__(name, dict(data), path)
        self._relation = _findRelation(self._data.keys())
        self._relationValue = _getNodeValue(self._data, self._relation)
        self._isNegative = False

    def negate(self):
        if self._relation is not None:
            self._relation = _RELATIONS.getOppositeRelation(self._relation)
        else:
            self._isNegative = not self._isNegative
        return

    def clearItemsCache(self):
        self._clearItemsCache()

    def _formatVehsTable(self, event = None):
        return []

    def _getLabelKey(self):
        return ''

    def _formatData(self, svrEvents, current = None, total = None, event = None):
        if self._isAnyVehicleAcceptable(self._data):
            if event is None or not event.isGuiDisabled():
                return formatters.packTextBlock(i18n.makeString('%s/all' % self._getLabelKey()), value=self._relationValue, relation=self._relation)
        elif 'types' not in self._data:
            if event is None or not event.isGuiDisabled():
                _, fNations, fLevels, fClasses = self._parseFilters(self._data)
                keys, kwargs = [], {}
                if fNations:
                    keys.append('nation')
                    kwargs['nation'] = ', '.join((i18n.makeString('#menu:nations/%s' % nations.NAMES[idx]) for idx in fNations))
                if fClasses:
                    keys.append('type')
                    kwargs['type'] = ', '.join([ i18n.makeString('#menu:classes/%s' % name) for name in fClasses ])
                if fLevels:
                    keys.append('level')
                    kwargs['level'] = ', '.join([ int2roman(lvl) for lvl in fLevels ])
                labelKey = '%s/%s' % (self._getLabelKey(), '_'.join(keys))
                if self._relationValue is None and self._isNegative:
                    labelKey = '%s/not' % labelKey
                if current is not None and total is not None:
                    return formatters.packTextCondition(i18n.makeString(labelKey, **kwargs), current=current, total=total)
                else:
                    return formatters.packTextBlock(i18n.makeString(labelKey, **kwargs), value=self._relationValue, relation=self._relation)
        else:
            subBlocks = []
            titleKey = self._getLabelKey()
            if self._isNegative:
                titleKey = '%s/not' % titleKey
            relation, value = self._relation, self._relationValue
            subBlocks.append(self._formatVehsTable(event=event))
            if len(subBlocks):
                if event is not None and event.isCompleted():
                    current, total = (None, None)
                return formatters.packContainer(i18n.makeString(titleKey), isResizable=True, isOpened=True, subBlocks=subBlocks, value=value, relation=relation, current=current, total=total)
        return

    def _format(self, svrEvents, event = None):
        fmtData = self._formatData(svrEvents, event=event)
        if fmtData is not None:
            return [fmtData]
        else:
            return []

    def _makeUniqueTableID(self, event):
        return formatters.makeUniqueTableID(event, self.getUniqueName())


class _VehsListRequirement(_VehsListCondition, _AvailabilityCheckable, _Negatable):

    def _isAvailable(self):
        vehsList = self._getVehiclesList(self._data)
        if self._relation is not None:
            return _handleRelation(self._relation, len(filter(self._checkVehicle, vehsList)), self._relationValue)
        else:
            for v in vehsList:
                if not self._checkVehicle(v):
                    return False

            return True

    def _checkVehicle(self, vehicle):
        return True

    def __repr__(self):
        return '%s<%s=%r>' % (self.__class__.__name__, self._relation, self._relationValue)


class AndGroup(_ConditionsGroup):

    def __init__(self, isNegative = False):
        super(AndGroup, self).__init__(GROUP_TYPE.AND, isNegative)

    def _formatSubBlocks(self, svrEvents, event = None):
        subBlocks = []
        for cond in self.getSortedItems():
            subBlocks.extend(cond.format(svrEvents, event))

        return subBlocks

    def _isAvailable(self, *args, **kwargs):
        res = True
        for cond in self.items:
            res = cond.isAvailable(*args, **kwargs)
            if not res:
                return res

        return res


class OrGroup(_ConditionsGroup):

    def __init__(self, isNegative = False):
        super(OrGroup, self).__init__(GROUP_TYPE.OR, isNegative)

    def _formatSubBlocks(self, svrEvents, event = None):
        subBlocks = []
        for cond in self.getSortedItems():
            subBlocks.extend(cond.format(svrEvents, event))

        result = []
        for idx, block in enumerate(subBlocks):
            result.append(block)
            if idx < len(subBlocks) - 1:
                result.append(formatters.packSeparator(makeHtmlString('html_templates:lobby/quests', 'or'), needAlign=True))

        return result

    def _isAvailable(self, *args, **kwargs):
        for cond in self.items:
            if cond.isAvailable(*args, **kwargs):
                return True

        return False


class IGR(_Requirement, _Updatable):

    def __init__(self, path, data):
        super(IGR, self).__init__('igrType', dict(data), path)
        self._igrTypes = {self._data.get('value')}

    def negate(self):
        igrTypes = constants.IGR_TYPE
        self._igrTypes ^= {igrTypes.BASE, igrTypes.PREMIUM}

    def update(self, other, groupType):
        if groupType == GROUP_TYPE.OR:
            if other.getName() == 'igrType':
                self._igrTypes |= other._igrTypes
                return True
        return False

    def _isAvailable(self):
        from gui import game_control
        return game_control.g_instance.igr.getRoomType() in self._igrTypes

    def _format(self, svrEvents, event = None):
        result = []
        if event is None or not event.isGuiDisabled():
            label = None
            igrTypes = constants.IGR_TYPE
            if constants.IS_CHINA or self._igrTypes.issuperset({igrTypes.BASE, igrTypes.PREMIUM}):
                label = 'igr'
            elif self._igrTypes & {igrTypes.BASE}:
                label = 'igrBasic'
            elif self._igrTypes & {igrTypes.PREMIUM}:
                label = 'igrPremium'
            if label is not None:
                result.append(formatters.packTextBlock(makeHtmlString('html_templates:lobby/quests', 'playInIgr', {'label': i18n.makeString('#quests:details/requirements/%s' % label)}), isAvailable=self.isAvailable()))
        return result

    def __repr__(self):
        return 'IGR<types=%s>' % self._igrTypes


class GlobalRating(_Requirement):

    def __init__(self, path, data):
        super(GlobalRating, self).__init__('GR', dict(data), path)
        self._relation = _findRelation(self._data.keys())
        self._relationValue = float(_getNodeValue(self._data, self._relation))

    def negate(self):
        self._relation = _RELATIONS.getOppositeRelation(self._relation)

    def _isAvailable(self):
        if self._relationValue is None:
            return False
        else:
            return _handleRelation(self._relation, g_itemsCache.items.stats.globalRating, self._relationValue)

    def _format(self, svrEvents, event = None):
        if event is None or not event.isGuiDisabled():
            return [formatters.packTextBlock(i18n.makeString('#quests:details/requirements/globalRating'), value=self._relationValue, relation=self._relation, isAvailable=self.isAvailable())]
        else:
            return []

    def __repr__(self):
        return 'GlobalRating<%s=%s>' % (self._relation, str(self._relationValue))


class PremiumAccount(_Requirement):

    def __init__(self, path, data):
        super(PremiumAccount, self).__init__('premiumAccount', dict(data), path)
        self._needValue = self._data.get('value')

    def negate(self):
        self._needValue = not self._needValue

    def _isAvailable(self):
        if self._needValue is not None:
            isPremium = account_helpers.isPremiumAccount(g_itemsCache.items.stats.attributes)
            return isPremium == self._needValue
        else:
            return True

    def _format(self, svrEvents, event = None):
        if event is None or not event.isGuiDisabled():
            labelKey = '#quests:details/requirements/%s' % ('premiumAccount' if self._needValue else 'notPremiumAccount')
            return [formatters.packTextBlock(i18n.makeString(labelKey), isAvailable=self.isAvailable())]
        else:
            return []

    def __repr__(self):
        return 'PremiumAccount<value=%r>' % self._needValue


class InClan(_Requirement):

    def __init__(self, path, data):
        super(InClan, self).__init__('inClan', dict(data), path)
        self._ids = _getNodeValue(self._data, 'ids')
        self._isNegative = False

    def negate(self):
        self._isNegative = not self._isNegative

    def _isAvailable(self):
        clanDBID = g_itemsCache.items.stats.clanDBID
        if self._ids is not None:
            if not self._isNegative:
                return clanDBID in self._ids
            else:
                return clanDBID not in self._ids
        return bool(clanDBID) != self._isNegative

    def _format(self, svrEvents, event = None):
        labelKey = None
        result = []
        if event is None or not event.isGuiDisabled():
            if self._ids is None:
                labelKey = 'notInAnyClan' if self._isNegative else 'inAnyClan'
            else:
                clanDBID = g_itemsCache.items.stats.clanDBID
                if not self._isNegative:
                    if clanDBID:
                        labelKey = 'forCurrentClan' if clanDBID in self._ids else 'notForCurrentClan'
                    else:
                        labelKey = 'inClan'
                elif clanDBID and clanDBID in self._ids:
                    labelKey = 'notForCurrentClan'
            if labelKey is not None:
                result.append(formatters.packTextBlock(i18n.makeString('#quests:details/requirements/%s' % labelKey), isAvailable=self.isAvailable()))
        return result

    def __repr__(self):
        return 'InClan<value=%r>' % self._ids


class Token(_Requirement):

    def __init__(self, path, data):
        super(Token, self).__init__('token', dict(data), path)
        self._id = _getNodeValue(self._data, 'id')
        self._consumable = 'consumable' in self._data
        self._relation = _findRelation(self._data.keys())
        self._relationValue = int(_getNodeValue(self._data, self._relation, 0))

    def getID(self):
        return self._id

    def negate(self):
        self._relation = _RELATIONS.getOppositeRelation(self._relation)

    def getNeededCount(self):
        if self._relation == _RELATIONS.GT:
            return self._relationValue + 1
        return self._relationValue

    def _isAvailable(self):
        return _handleRelation(self._relation, self.__getTokensCount(), self._relationValue)

    def _format(self, svrEvents, event = None):
        result = []
        for eID, e in svrEvents.iteritems():
            if e.getType() in (constants.EVENT_TYPE.BATTLE_QUEST, constants.EVENT_TYPE.TOKEN_QUEST, constants.EVENT_TYPE.FORT_QUEST):
                children = e.getChildren()
                if self._id in children:
                    for qID in children[self._id]:
                        quest = svrEvents.get(qID)
                        if quest is not None:
                            isAvailable = True
                            if event is not None and not event.isCompleted():
                                isAvailable = self.isAvailable()
                            tokensCountNeed = self.getNeededCount()
                            battlesLeft = None
                            if tokensCountNeed > 1:
                                label = i18n.makeString('#quests:details/requirements/token/N', count=BigWorld.wg_getIntegralFormat(tokensCountNeed), questName=quest.getUserName())
                                if not isAvailable:
                                    battlesLeft = tokensCountNeed - self.__getTokensCount()
                            else:
                                label = i18n.makeString('#quests:details/requirements/token', questName=quest.getUserName())
                            counterDescr = None
                            if e.getType() != constants.EVENT_TYPE.TOKEN_QUEST:
                                counterDescr = i18n.makeString('#quests:quests/table/battlesLeft')
                            result.append(formatters.packTextBlock(label, questID=qID, isAvailable=isAvailable, counterValue=battlesLeft, counterDescr=counterDescr))
                        else:
                            LOG_WARNING('Unknown quest id in token conditions', qID)

        return result

    def __getTokensCount(self):
        from gui.server_events import g_eventsCache
        return g_eventsCache.questsProgress.getTokenCount(self._id)

    def __repr__(self):
        return 'Token<id=%s; %s=%d; consumable=%r>' % (self._id,
         self._relation,
         self._relationValue,
         self._consumable)


class VehiclesUnlocked(_VehsListRequirement):

    def __init__(self, path, data):
        super(VehiclesUnlocked, self).__init__('vehiclesUnlocked', dict(data), path)

    def _checkVehicle(self, vehicle):
        return vehicle.isUnlocked

    def _getLabelKey(self):
        return '#quests:details/requirements/vehiclesUnlocked'

    def _formatVehsTable(self, event = None):
        return formatters.packVehiclesBlock(self._makeUniqueTableID(event), formatters.VEH_UNLOCKS_HEADER, disableChecker=lambda v: not v.isUnlocked, vehs=_prepareVehData(self._getVehiclesList(self._data)))


class VehiclesOwned(_VehsListRequirement):

    def __init__(self, path, data):
        super(VehiclesOwned, self).__init__('vehiclesOwned', dict(data), path)

    def _checkVehicle(self, vehicle):
        return vehicle.isInInventory

    def _getLabelKey(self):
        return '#quests:details/requirements/vehiclesOwned'

    def _formatVehsTable(self, event = None):
        return formatters.packVehiclesBlock(self._makeUniqueTableID(event), formatters.VEH_OWNED_HEADER, disableChecker=lambda v: not v.isInInventory, vehs=_prepareVehData(self._getVehiclesList(self._data)), showInHangarCB=True, isShowInHangarCBChecked=False)


class PremiumVehicle(_VehicleRequirement):

    def __init__(self, path, data):
        super(PremiumVehicle, self).__init__('premiumVehicle', dict(data), path)
        self._needValue = self._data.get('value')

    def negate(self):
        self._needValue = not self._needValue

    def _isAvailable(self, vehicle):
        return vehicle.isPremium == self._needValue

    def __repr__(self):
        return 'PremiumVehicle<value=%r>' % self._needValue


class XPMultipliedVehicle(_VehicleRequirement):

    def __init__(self, path, data):
        super(XPMultipliedVehicle, self).__init__('hasReceivedMultipliedXP', dict(data), path)
        self._needValue = self._data.get('value')

    def negate(self):
        self._needValue = not self._needValue

    def _format(self, svrEvents, event = None):
        result = []
        if event is None or not event.isGuiDisabled():
            key = '#quests:details/requirements/vehicle/%s' % ('receivedMultXp' if self._needValue else 'notReceivedMultXp')
            result.append(formatters.packTextBlock(i18n.makeString(key, mult=g_itemsCache.items.shop.dailyXPFactor)))
        return result

    def _isAvailable(self, vehicle):
        return (vehicle.dailyXPFactor == -1) == self._needValue

    def __repr__(self):
        return 'XPMultipliedVehicle<value=%r>' % self._needValue


class VehicleDescr(_VehicleRequirement, _VehsListParser, _Updatable):

    def __init__(self, path, data, vehReqs):
        super(VehicleDescr, self).__init__('vehicleDescr', dict(data), path)
        self._otherCriteria = REQ_CRITERIA.EMPTY
        self._isNegative = False
        self._isMultXpReceived = None
        self._isPremium = None
        self._vehReqs = weakref.proxy(vehReqs)
        return

    def clearItemsCache(self):
        self._clearItemsCache()

    def negate(self):
        self._isNegative = not self._isNegative

    def isAnyVehicleAcceptable(self):
        return self._isAnyVehicleAcceptable(self._data)

    def update(self, other, groupType):
        if groupType != GROUP_TYPE.AND:
            return False
        if other.getName() == 'vehicleDescr':
            self._otherCriteria |= other._getFilterCriteria(other._data)
            return True
        if other.getName() == 'hasReceivedMultipliedXP':
            self._isMultXpReceived = other._needValue
        elif other.getName() == 'premiumVehicle':
            self._isPremium = other._needValue
        return False

    def getVehiclesList(self):
        return self._getVehiclesList(self._data)

    def _preProcessCriteria(self, criteria):
        if self._isPremium is not None:
            if self._isPremium:
                criteria |= REQ_CRITERIA.VEHICLE.PREMIUM
            else:
                criteria |= ~REQ_CRITERIA.VEHICLE.PREMIUM
        if self._isNegative:
            return ~criteria | ~REQ_CRITERIA.SECRET
        else:
            return criteria | self._otherCriteria

    def _isAvailable(self, vehicle):
        return vehicle in self._getVehiclesList(self._data)

    def _format(self, svrEvents, event = None):
        predicate = None
        if self._vehReqs is not None:
            predicate = self._vehReqs.isAvailable
        return [formatters.packVehiclesBlock(formatters.makeUniqueTableID(event, self.getUniqueName()), formatters.VEH_REQUIRED_HEADER, disableChecker=lambda v: not v.isInInventory, vehs=_prepareVehData(self._getVehiclesList(self._data), predicate), showInHangarCB=True, isShowInHangarCBChecked=True)]


class _DossierValue(_Requirement):

    def __init__(self, name, data, path):
        super(_DossierValue, self).__init__(name, dict(data), path)
        self._recordName = _getNodeValue(self._data, 'record', '').split(':')
        self._average = 'average' in self._data
        self._relation = _findRelation(self._data.keys())
        self._relationValue = float(_getNodeValue(self._data, self._relation, 0.0))

    def negate(self):
        self._relation = _RELATIONS.getOppositeRelation(self._relation)

    def _checkDossier(self, dossier):
        block, record = self._recordName
        dossierDescr = dossier.getDossierDescr()
        dossierValue = dossierDescr[block][record]
        if self._average:
            battlesCount = dossier.getRandomStats().getBattlesCount()
            dossierValue /= float(battlesCount or 1)
        return _handleRelation(self._relation, dossierValue, self._relationValue)

    def _getFmtValues(self):
        i18nLabel = i18n.makeString('#quests:details/requirements/%s' % ('dossierValue' if not self._average else 'dossierAvgValue'), label=self.__getLabelKey())
        return (i18nLabel, self._relationValue, self._relation)

    def __getLabelKey(self):
        _, record = self._recordName
        battleMode = self.__dossierBlock2BattleMode()
        if len(battleMode):
            return i18n.makeString('#quests:details/dossier/%s/%s' % (battleMode, record))
        return i18n.makeString('#quests:details/dossier/%s' % record)

    def __dossierBlock2BattleMode(self):
        block, _ = self._recordName
        if block in ('a15x15', 'a15x15_2'):
            return 'random'
        if block in ('company', 'company2'):
            return 'company'
        if block in ('clan', 'clan2'):
            return 'clan'
        if block in ('a7x7',):
            return 'team'
        if block in ('historical',):
            return 'historical'
        if block in ('achievements',):
            return 'achievements'
        return ''

    def __repr__(self):
        return '%s<record=%s; average=%r; %s=%.2f>' % (self.__class__.__name__,
         self._recordName,
         self._average,
         self._relation,
         self._relationValue)


class AccountDossierValue(_DossierValue):

    def __init__(self, path, data):
        super(AccountDossierValue, self).__init__('accountDossier', dict(data), path)

    def _isAvailable(self):
        return self._checkDossier(g_itemsCache.items.getAccountDossier())

    def _format(self, svrEvents, event = None):
        if event is None or not event.isGuiDisabled():
            label, value, relation = self._getFmtValues()
            return [formatters.packTextBlock(label, value=value, relation=relation, isAvailable=self.isAvailable())]
        else:
            return []


class VehicleDossierValue(_DossierValue):

    def __init__(self, path, data):
        super(VehicleDossierValue, self).__init__('vehicleDossier', dict(data), path)

    def _isAvailable(self, vehicle):
        return self._checkDossier(g_itemsCache.items.getVehicleDossier(vehicle.intCD))

    def _format(self, svrEvents, event = None):
        if event is None or not event.isGuiDisabled():
            label, value, relation = self._getFmtValues()
            return [formatters.packTextBlock(label, value=value, relation=relation)]
        else:
            return []


class BattleBonusType(_Condition, _Negatable):

    def __init__(self, path, data):
        super(BattleBonusType, self).__init__('bonusTypes', dict(data), path)
        self._types = self._data.get('value')

    def negate(self):
        newTypes = []
        for bt in constants.ARENA_BONUS_TYPE.RANGE:
            if bt not in self._types:
                newTypes.append(bt)

        self._types = newTypes

    def getValue(self):
        return self._types

    def _format(self, svrEvents, event = None):
        if event is None or not event.isGuiDisabled():
            return [formatters.packIconTextBlock(formatters.formatGray('#quests:details/conditions/battleBonusType'), iconTexts=[ formatters.packBonusTypeElement(bt) for bt in self._types ])]
        else:
            return []

    def __repr__(self):
        return 'BonusType<types=%r>' % self._types


class BattleSquad(_Condition, _Negatable):

    def __init__(self, path, data):
        super(BattleSquad, self).__init__('isSquad', dict(data), path)
        self._isSquad = self._data.get('value')

    def negate(self):
        self._isSquad = not self._isSquad

    def getValue(self):
        return self._isSquad

    def _format(self, svrEvents, event = None):
        result = []
        if event is None or not event.isGuiDisabled():
            if self._isSquad:
                result.append(formatters.packIconTextBlock(formatters.formatGray('#quests:details/conditions/formation'), iconTexts=[formatters.packFormationElement('squad')]))
            else:
                result.append(formatters.packTextBlock('#quests:details/conditions/notSquad'))
        return result

    def __repr__(self):
        return 'BattleSquad<isSquad=%r>' % self._isSquad


class BattleClanMembership(_Condition, _Negatable):

    class VALUES(CONST_CONTAINER):
        ANY = 'any'
        SAME = 'same'

    def __init__(self, path, data, preBattleCondProxy = None):
        super(BattleClanMembership, self).__init__('clanMembership', dict(data), path)
        self._value = self._data.get('value')
        self.__proxy = weakref.proxy(preBattleCondProxy)

    def negate(self):
        pass

    def _format(self, svrEvents, event = None):
        result = []
        if event is None or not event.isGuiDisabled():
            result.append(formatters.packTextBlock('#quests:details/conditions/clanMembership/%s/%s' % (self._value, _getArenaBonusType(self.__proxy))))
        return result

    def __repr__(self):
        return 'BattleClanMembership<relation=%r; bonusType=%s>' % (self._value, _getArenaBonusType(self.__proxy))


class HistoricalBattles(_Condition, _Negatable):

    def __init__(self, path, data):
        super(HistoricalBattles, self).__init__('historicalBattleIDs', dict(data), path)
        self._battlesIDs = self._data.get('value')

    def negate(self):
        pass

    def _format(self, svrEvents, event = None):
        result = []
        if event is None or not event.isGuiDisabled():
            result.append(formatters.packIconTextBlock(formatters.formatGray('#quests:details/conditions/historicalBattles'), iconTexts=[ formatters.packHistoricalBattleElement(bID) for bID in self._battlesIDs ]))
        return result

    def __repr__(self):
        return 'HistoricalBattles<value=%r>' % self._battlesIDs


class BattleCamouflage(_Condition, _Negatable):

    def __init__(self, path, data):
        super(BattleCamouflage, self).__init__('camouflageKind', dict(data), path)
        self._camos = self._data.get('value')

    def negate(self):
        newCamos = []
        for camoTypeName, camoID in vehicles.CAMOUFLAGE_KINDS.iteritems():
            if camoID not in self._camos:
                newCamos.append(camoID)

        self._camos = newCamos

    def _format(self, svrEvents, event = None):
        result = []
        if event is None or not event.isGuiDisabled():
            camos = []
            for camoTypeName, camoID in vehicles.CAMOUFLAGE_KINDS.iteritems():
                if camoID in self._camos:
                    camos.append(formatters.packCamoElement(camoTypeName))

            if len(camos):
                result.append(formatters.packIconTextBlock(formatters.formatGray('#quests:details/conditions/mapsType'), iconTexts=camos))
        return result

    def __repr__(self):
        return 'BattleCamouflage<camos=%r>' % self._camos


class BattleMap(_Condition, _Negatable):

    def __init__(self, path, data):
        super(BattleMap, self).__init__('geometryNames', dict(data), path)
        self._maps = self._data.get('value')
        self._isNegative = False

    def negate(self):
        self._isNegative = not self._isNegative

    def _format(self, svrEvents, event = None):
        if event is not None and event.isGuiDisabled():
            return []
        else:
            maps = []
            for atID in self._maps:
                fmt = formatters.packMapElement(atID)
                if fmt is not None:
                    maps.append(fmt)

            key = 'maps' if len(maps) > 1 else 'map'
            if self._isNegative:
                key = '%s/not' % key
            return [formatters.packIconTextBlock(formatters.formatGray('#quests:details/conditions/%s' % key), iconTexts=sorted(maps, key=operator.methodcaller('getLabel')))]

    def __repr__(self):
        return 'BattleMap<maps=%r>' % self._maps


class Win(_Condition, _Negatable):

    def __init__(self, path, data):
        super(Win, self).__init__('win', dict(data), path)
        self._isWin = self._data.get('value')

    def negate(self):
        self._isWin = not self._isWin

    def getValue(self):
        return self._isWin

    def _format(self, svrEvents, event = None):
        result = []
        if event is None or not event.isGuiDisabled():
            key = 'win' if self._isWin else 'notWin'
            result.append(formatters.packTextBlock(i18n.makeString('#quests:details/conditions/%s' % key)))
        return result

    def __repr__(self):
        return 'Win<value=%r>' % self._isWin


class Survive(_Condition, _Negatable):

    def __init__(self, path, data):
        super(Survive, self).__init__('isAlive', dict(data), path)
        self._isAlive = self._data.get('value')

    def negate(self):
        self._isAlive = not self._isAlive

    def _format(self, svrEvents, event = None):
        result = []
        if event is None or not event.isGuiDisabled():
            key = 'survive' if self._isAlive else 'notSurvive'
            result.append(formatters.packTextBlock(i18n.makeString('#quests:details/conditions/%s' % key)))
        return result

    def __repr__(self):
        return 'Survive<value=%r>' % self._isAlive


class Achievements(_Condition, _Negatable, _Updatable):

    def __init__(self, path, data):
        super(Achievements, self).__init__('achievements', dict(data), path)
        self._achieves = set(self._data.get('value'))
        self._isNegative = False

    def negate(self):
        self._isNegative = not self._isNegative

    def update(self, other, groupType):
        if groupType == GROUP_TYPE.OR and other.getName() == 'achievements':
            self._achieves |= other._achieves
            return True
        return False

    def _format(self, svrEvents, event = None):
        if event is not None and event.isGuiDisabled():
            return []
        else:
            key = 'oneAchievement' if len(self._achieves) == 1 else 'achievements'
            if self._isNegative:
                key = '%s/not' % key
            return [formatters.packIconTextBlock(formatters.formatBright('#quests:details/conditions/%s' % key), iconTexts=[ formatters.packAchieveElement(idx) for idx in self._achieves ])]

    def __repr__(self):
        return 'Achievements<idx=%r>' % self._achieves


class ClanKills(_Condition, _Negatable):

    def __init__(self, path, data):
        super(ClanKills, self).__init__('clanKills', dict(data), path)
        self._camos2ids = {}
        self._isNegative = False
        for camoName, ids in data:
            self._camos2ids[camoName] = ids

    def negate(self):
        self._isNegative = not self._isNegative

    def format(self, svrEvents, event = None):
        result = []
        if event is None or not event.isGuiDisabled():
            camos = []
            for camo in self._camos2ids.keys():
                camoI18key = '#quests:details/conditions/clanKills/camo/%s' % str(camo)
                if i18n.doesTextExist(camoI18key):
                    camos.append(i18n.makeString(camoI18key))

            i18nKey = '#quests:details/conditions/clanKills'
            if self._isNegative:
                i18nKey = '%s/not' % i18nKey
            if len(camos):
                result = [formatters.packTextBlock(i18n.makeString(i18nKey, camos=', '.join(camos)))]
        return result

    def __repr__(self):
        return 'ClanKills<camos=%r>' % str(self._camos2ids)


class _Cumulativable(_Condition):
    __metaclass__ = ABCMeta

    def getProgressPerGroup(self, curProgData = None, prevProgData = None):
        return self._parseProgress(curProgData, prevProgData)

    def formatByGroup(self, svrEvents, groupByKey, event = None):
        return self._formatByGroup(svrEvents, groupByKey, event)

    def getUserString(self):
        return ''

    def _formatByGroup(self, svrEvents, groupByKey, event = None):
        return []

    @abstractmethod
    def _getKey(self):
        pass

    @abstractmethod
    def _getTotalValue(self):
        pass

    @abstractmethod
    def _getBonusData(self):
        pass

    def _parseProgress(self, curProgData, prevProgData):
        result = {}
        bonus = self._getBonusData()
        curProgData = bonus.getProgress() if curProgData is None else curProgData
        if bonus is None:
            return result
        else:
            key = self._getKey()
            groupBy = bonus.getGroupByValue()
            total = self._getTotalValue()
            if groupBy is None:
                diff = 0
                curProg = curProgData.get(None, {})
                current = min(curProg.get(key, 0), total)
                if prevProgData is not None:
                    prevProg = prevProgData.get(None, {})
                    diff = current - min(prevProg.get(key, 0), total)
                result[None] = (min(curProg.get(key, 0), total),
                 total,
                 diff,
                 self.__isProgressCompleted(curProg))
            else:
                for gByKey, progress in curProgData.iteritems():
                    diff = 0
                    current = min(progress.get(key, 0), total)
                    if prevProgData is not None:
                        prevProg = prevProgData.get(gByKey, {})
                        diff = current - min(prevProg.get(key, 0), total)
                    result[gByKey] = (current,
                     total,
                     diff,
                     self.__isProgressCompleted(progress))

            return result

    def __getProgDiff(self, curProg, prevProg):
        if prevProg is None:
            return 0
        else:
            key = self._getKey()
            return curProg.get(key, 0) - prevProg.get(key, 0)

    def __isProgressCompleted(self, progress):
        bonusLimit = self._getBonusData().getBonusLimit()
        if bonusLimit is not None:
            return progress.get('bonusCount', 0) >= bonusLimit
        else:
            return False


class BattlesCount(_Cumulativable):

    def __init__(self, path, data, bonusCond):
        super(BattlesCount, self).__init__('battles', dict(data), path)
        self._bonus = weakref.proxy(bonusCond)

    def getUserString(self):
        return i18n.makeString('#quests:details/dossier/random/battlesCount')

    def _getKey(self):
        return 'battlesCount'

    def _getTotalValue(self):
        return _getNodeValue(self._data, 'count', 0)

    def _getBonusData(self):
        return self._bonus

    def __repr__(self):
        return 'BattlesCount<key=%s; total=%d>' % (self._getKey(), self._getTotalValue())


class BattleResults(_Condition, _Negatable, _Updatable):
    TOP_RANGE_HIGHEST = 1
    TOP_RANGE_LOWEST = 15

    def __init__(self, path, data, localeKey = 'single'):
        super(BattleResults, self).__init__('results', dict(data), path)
        self._keyName = _getNodeValue(self._data, 'key')
        self._max = (self.TOP_RANGE_HIGHEST, int(_getNodeValue(self._data, 'max', self.TOP_RANGE_LOWEST)))
        self._isTotal = 'total' in self._data
        self._isAvg = 'average' in self._data
        self._relation = _findRelation(self._data.keys())
        self._relationValue = _getNodeValue(self._data, self._relation)
        self._localeKey = localeKey
        self._isNegative = False

    def getTopRange(self):
        if not self._isNegative:
            return self._max
        return (min(self._max[1] + 1, self.TOP_RANGE_LOWEST), self.TOP_RANGE_LOWEST)

    def update(self, other, groupType):
        if groupType == GROUP_TYPE.AND:
            if other.getName() == 'results' and self._keyName == other._keyName:
                topRange, otherTopRange = self.getTopRange(), other.getTopRange()
                self._max = (max(topRange[0], otherTopRange[0]), min(topRange[1], otherTopRange[1]))
                return True
        return False

    def negate(self):
        self._relation = _RELATIONS.getOppositeRelation(self._relation)
        self._isNegative = not self._isNegative

    def format(self, svrEvents, event = None):

        def _makeStr(i18nKey, *args, **kwargs):
            if self._isNegative:
                i18nKey = '%s/not' % i18nKey
            return i18n.makeString(i18nKey, *args, **kwargs)

        if event is not None and event.isGuiDisabled():
            return []
        else:
            key = i18n.makeString('#quests:details/conditions/cumulative/%s' % self._keyName)
            labelKey = '#quests:details/conditions/results'
            topRangeUpper, topRangeLower = self._max
            if topRangeLower < self.TOP_RANGE_LOWEST:
                labelKey = '%s/%s/%s' % (labelKey, self._localeKey, 'bothTeams' if self._isTotal else 'halfTeam')
                if topRangeUpper == self.TOP_RANGE_HIGHEST:
                    label = _makeStr('%s/top' % labelKey, param=key, count=topRangeLower)
                elif topRangeLower == topRangeUpper:
                    label = _makeStr('%s/position' % labelKey, param=key, position=topRangeUpper)
                else:
                    label = _makeStr('%s/range' % labelKey, param=key, high=topRangeUpper, low=topRangeLower)
            elif self._isAvg:
                label = i18n.makeString('#quests:details/conditions/results/%s/avg' % self._localeKey, param=key)
            else:
                label = i18n.makeString('#quests:details/conditions/results/%s/simple' % self._localeKey, param=key)
            value, relation, relationI18nType = self._relationValue, self._relation, _RELATIONS_SCHEME.DEFAULT
            if self._keyName == 'markOfMastery':
                relationI18nType = _RELATIONS_SCHEME.ALTERNATIVE
                if self._relationValue == 0:
                    if self._relation in (_RELATIONS.EQ, _RELATIONS.LSQ):
                        i18nLabelKey = '#quests:details/conditions/cumulative/markOfMastery0'
                    else:
                        if self._relation in (_RELATIONS.LS,):
                            raise Exception('Mark of mastery 0 can be used with greater or equal relation types')
                        i18nLabelKey = '#quests:details/conditions/cumulative/markOfMastery0/not'
                    label, value, relation = i18n.makeString(i18nLabelKey), None, None
                else:
                    i18nValueKey = '#quests:details/conditions/cumulative/markOfMastery%d' % int(self._relationValue)
                    i18nLabel = i18n.makeString('#quests:details/conditions/cumulative/markOfMastery')
                    label, value, relation = i18nLabel, i18n.makeString(i18nValueKey), self._relation
            return [formatters.packTextBlock(label, value=value, relation=relation, relationI18nType=relationI18nType)]

    def __repr__(self):
        return 'BattleResults<key=%s; %s=%r; max=%r; total=%r; avg=%r>' % (self._keyName,
         self._relation,
         self._relationValue,
         self._max,
         self._isTotal,
         self._isAvg)


class UnitResults(_Condition, _Negatable):

    def __init__(self, path, data, preBattleCond = None):
        super(UnitResults, self).__init__('unitResults', dict(data), path)
        self._isAllAlive = _getNodeValue(self._data, 'allAlive')
        unitKey = _getArenaBonusType(preBattleCond)
        self._results = []
        for idx, (keyName, value) in enumerate(data):
            resultData, isNegative = None, False
            if keyName == 'not' and len(value):
                (_, resultData), isNegative = value[0], not isNegative
            elif keyName == 'results':
                resultData = value
            if resultData is not None:
                results = BattleResults('%s.battleResults%d' % (path, idx), resultData, localeKey=unitKey)
                if isNegative:
                    results.negate()
                self._results.append(results)

        return

    def negate(self):
        self._isAllAlive = not self._isAllAlive
        for result in self._results:
            result.negate()

    def _format(self, svrEvents, event = None):
        results = []
        if event is None or not event.isGuiDisabled():
            if self._isAllAlive is not None:
                key = 'alive' if self._isAllAlive else 'alive/not'
                results.append(formatters.packTextBlock(i18n.makeString('#quests:details/conditions/results/unit/%s' % key)))
            for r in self._results:
                results.extend(r.format(svrEvents, event))

        return results

    def __repr__(self):
        return 'UnitResults<resultsCount=%d>' % len(self._results)


class CumulativeResult(_Cumulativable):

    def __init__(self, path, data, bonusCond, isUnit = False, preBattleCond = None):
        super(CumulativeResult, self).__init__('cumulative', dict(data), path)
        self._bonus = weakref.proxy(bonusCond)
        self._key, self._total = self._data.get('value', (None, 0))
        self._isUnit = isUnit
        self._unitName = _getArenaBonusType(preBattleCond)
        return None

    def getUserString(self):
        return self.__getLabelString()

    def _getKey(self):
        if self._isUnit:
            return 'unit_%s' % self._key
        return self._key

    def _getTotalValue(self):
        return self._total

    def _getBonusData(self):
        return self._bonus

    def _format(self, svrEvents, event = None):
        result = []
        if event is None or not event.isGuiDisabled():
            result.append(formatters.packTextCondition(self.__getLabelString(), value=self._getTotalValue()))
        return result

    def _formatByGroup(self, svrEvents, groupByKey, event = None):
        result = []
        progress = self.getProgressPerGroup()
        if groupByKey in progress:
            if event is None or not event.isGuiDisabled():
                current, total, _, isGroupCompleted = progress[groupByKey]
                if event is not None and event.isCompleted() or isGroupCompleted:
                    result.append(formatters.packTextCondition(self.__getLabelString(), value=self._getTotalValue()))
                else:
                    isConditionCompleted = False
                    if current is not None and total is not None:
                        isConditionCompleted = current >= total
                    result.append(formatters.packTextCondition(self.__getLabelString(), current=current, total=total, isCompleted=isConditionCompleted))
        return result

    def __getLabelString(self):
        param = i18n.makeString('#quests:details/conditions/cumulative/%s' % self._key)
        if self._isUnit:
            label = '#quests:details/conditions/cumulative/%s' % self._unitName
        else:
            label = '#quests:details/conditions/cumulative/single'
        return i18n.makeString(label, param=param)

    def __repr__(self):
        return 'CumulativeResult<key=%s; total=%d>' % (self._getKey(), self._getTotalValue())


class VehicleKills(_VehsListCondition):

    def __init__(self, path, data):
        super(VehicleKills, self).__init__('vehicleKills', dict(data), path)

    def _getLabelKey(self):
        return '#quests:details/conditions/vehiclesKills'

    def _formatVehsTable(self, event = None):
        return formatters.packVehiclesBlock(self._makeUniqueTableID(event), formatters.VEH_KILLS_HEADER, vehs=_prepareVehData(self._getVehiclesList(self._data)))

    def __repr__(self):
        return 'VehicleKills<%s=%d>' % (self._relation, self._relationValue)


class VehicleKillsCumulative(_Cumulativable, VehicleKills):

    def __init__(self, path, data, bonusCond):
        super(VehicleKills, self).__init__('vehicleKillsCumulative', dict(data), path)
        self._bonus = weakref.proxy(bonusCond)

    def getUserString(self):
        return i18n.makeString(self._getLabelKey())

    def _getKey(self):
        return 'vehicleKills'

    def _getTotalValue(self):
        return self._relationValue

    def _getBonusData(self):
        return self._bonus

    def _formatByGroup(self, svrEvents, groupByKey, event = None):
        if self._bonus is not None:
            progress = self.getProgressPerGroup()
            if groupByKey in progress:
                current, total, _, _ = progress[groupByKey]
                if event is not None and event.isCompleted():
                    current, total = (None, None)
                if self._bonus.getGroupByValue() is not None:
                    return [formatters.packTextCondition(i18n.makeString(self._getLabelKey()), relation=self._relation, value=self._relationValue, current=current, total=total)]
                fmtData = self._formatData(svrEvents, current, total, event=event)
                if fmtData is not None:
                    return [fmtData]
        return []

    def __repr__(self):
        return 'VehicleKills<key=%s; %s=%d; total=%d>' % (self._getKey(),
         self._relation,
         self._relationValue,
         self._getTotalValue())


class RefSystemRalXPPoolCondition(_Requirement):

    def __init__(self, path, data):
        super(RefSystemRalXPPoolCondition, self).__init__('refSystemRalXPPool', dict(data), path)
        self._relation = _findRelation(self._data.keys())
        self._relationValue = float(_getNodeValue(self._data, self._relation))

    def negate(self):
        self._relation = _RELATIONS.getOppositeRelation(self._relation)

    def getValue(self):
        return self._relationValue

    def __repr__(self):
        return 'RefSystemRalXPPoolCondition<%s=%s>' % (self._relation, str(self._relationValue))


class RefSystemRalBought10Lvl(_Requirement):

    def __init__(self, path, data):
        super(RefSystemRalBought10Lvl, self).__init__('refSystemRalBought10Lvl', dict(data), path)
        self._relation = bool(self._data['value'])

    def negate(self):
        self._relation = not self._relation

    def getValue(self):
        return self._relation

    def __repr__(self):
        return 'RefSystemRalBought10Lvl<value=%r>' % self._relation
