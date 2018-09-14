# Embedded file name: scripts/client/gui/server_events/parsers.py
import weakref
from collections import defaultdict
from constants import EVENT_TYPE
from helpers import i18n
from gui import makeHtmlString, GUI_NATIONS_ORDER_INDEX
from gui.server_events import formatters, conditions
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES

class ConditionsParser(object):
    LOGICAL_OPS = {'and': conditions.AndGroup,
     'or': conditions.OrGroup}
    NEGATIVE_OP = 'not'

    def __init__(self, section, rootName = ''):
        self._section = section
        self._rootNode = None
        self.__rootName = rootName
        return

    def getConditions(self):
        if self._rootNode is None:
            self._rootNode = self._parse()
        return self._rootNode

    def clearCache(self):
        self._rootNode = None
        return

    def forEachNodeInTree(self, handler):
        raise handler is not None or AssertionError
        self.__forEachNode(self.getConditions(), handler)
        return

    def format(self, svrEvents, event = None):
        conds = self.getConditions()
        if not conds.isEmpty():
            return formatters.packTopLevelContainer(subBlocks=conds._formatSubBlocks(svrEvents, event))
        else:
            return None

    def _handleCondition(self, name, data, uniqueName, group):
        return None

    def _parse(self):
        if len(self._section) <= 0:
            return conditions.AndGroup()
        startParsingPoint = self._section
        unionOps = set(self.LOGICAL_OPS.keys()).intersection(dict(self._section).keys())
        if len(unionOps):
            rootGroup = self.LOGICAL_OPS[unionOps.pop()]()
            startParsingPoint = self._section[0][1]
        else:
            rootGroup = conditions.AndGroup()
        self._parseNode(self.__rootName, startParsingPoint, rootGroup)
        return rootGroup

    def _parseNode(self, uniquePath, section, group, isNegative = False):
        for idx, (nodeName, nodeData) in enumerate(section):
            newNode = None
            uniqueName = formatters.makeUniquePath(uniquePath, nodeName)
            if nodeName in self.LOGICAL_OPS:
                newNode = self.LOGICAL_OPS[nodeName](isNegative)
                self._parseNode(uniqueName, nodeData, newNode)
            elif nodeName == self.NEGATIVE_OP:
                self._parseNode(uniqueName, nodeData, group, True)
            else:
                if group.find(nodeName) is not None:
                    uniqueName = '%s%d' % (uniqueName, idx)
                newNode = self._handleCondition(nodeName, nodeData, uniqueName, group)
                if newNode is not None and isNegative:
                    newNode.negate()
            if newNode is not None:
                group.add(newNode)

        return

    def __forEachNode(self, group, handler):
        if group.isEmpty() is None:
            return
        else:
            for node in group.items:
                if isinstance(node, conditions._ConditionsGroup):
                    self.__forEachNode(node, handler)
                else:
                    handler(node)

            return


class AccountRequirements(ConditionsParser):

    def __init__(self, questType, section):
        super(AccountRequirements, self).__init__(section, rootName='account')
        self._hasIgrCondition = False
        self._questType = questType

    def getConditions(self):
        rootNode = super(AccountRequirements, self).getConditions()
        if self._questType == EVENT_TYPE.CLUBS_QUEST and not rootNode.find('hasClub'):
            rootNode.add(conditions.HasClub(formatters.makeUniquePath('root', 'hasClub')))
        return rootNode

    def clearItemsCache(self):
        self.forEachNodeInTree(lambda node: node.clearItemsCache())

    def _handleCondition(self, name, data, uniqueName, group):
        if name == 'token':
            return conditions.Token(uniqueName, data)
        if name == 'premium':
            return conditions.PremiumAccount(uniqueName, data)
        if name == 'inClan':
            return conditions.InClan(uniqueName, data)
        if name == 'igrType':
            self._hasIgrCondition = True
            return conditions.IGR(uniqueName, data)
        if name == 'GR':
            return conditions.GlobalRating(uniqueName, data)
        if name == 'dossier':
            return conditions.AccountDossierValue(uniqueName, data)
        if name == 'vehiclesUnlocked':
            return conditions.VehiclesUnlocked(uniqueName, data)
        if name == 'vehiclesOwned':
            return conditions.VehiclesOwned(uniqueName, data)
        if name == 'refSystemRalXPPool':
            return conditions.RefSystemRalXPPoolCondition(uniqueName, data)
        if name == 'refSystemRalBought10Lvl':
            return conditions.RefSystemRalBought10Lvl(uniqueName, data)

    def isAvailable(self):
        conds = self.getConditions()
        if not conds.isEmpty():
            return conds.isAvailable()
        return True

    def hasIGRCondition(self):
        self.getConditions()
        return self._hasIgrCondition

    def getTokens(self):
        results = []

        def handler(node):
            if node.getName() == 'token':
                results.append(node)

        self.forEachNodeInTree(handler)
        return results

    def format(self, svrEvents, event = None):
        subBlocks = self.getConditions()._formatSubBlocks(svrEvents, event)
        if len(subBlocks):
            return formatters.packTopLevelContainer(title=i18n.makeString('#quests:details/tasks/requirements/accountLabel'), subBlocks=subBlocks)
        else:
            return None


class VehicleRequirements(ConditionsParser):

    def __init__(self, section):
        super(VehicleRequirements, self).__init__(section, rootName='vehicle')

    def clearItemsCache(self):
        self.forEachNodeInTree(lambda node: node.clearItemsCache())

    def isAvailable(self, vehicle):
        conds = self.getConditions()
        if not conds.isEmpty():
            return conds.isAvailable(vehicle)
        return True

    def isAnyVehicleAcceptable(self):
        results = set()

        def handler(node):
            if node.getName() == 'vehicleDescr':
                results.add(node.isAnyVehicleAcceptable())
            elif node.getName() in ('premiumVehicle', 'hasReceivedMultipliedXP'):
                results.add(False)

        self.forEachNodeInTree(handler)
        return False not in results

    def getSuitableVehicles(self):
        from gui.shared import g_itemsCache, REQ_CRITERIA
        invVehs = g_itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()
        return [ v for v in invVehs if self.isAvailable(v) ]

    def format(self, svrEvents, event = None):
        conds = self.getConditions()
        if conds.isEmpty():
            subBlocks = [formatters.packTextBlock(i18n.makeString('#quests:details/requirements/vehicle/any'))]
        else:
            subBlocks = conds._formatSubBlocks(svrEvents, event)
        title, note = i18n.makeString('#quests:details/tasks/requirements/vehicleLabel'), ''
        if conds:
            vehDescr = conds.find('vehicleDescr')
            if vehDescr is not None:
                note = makeHtmlString('html_templates:lobby/quests', 'vehicleDescrLabel', {'count': len(self.getSuitableVehicles()),
                 'total': len(vehDescr.getVehiclesList())})
        if len(subBlocks):
            return formatters.packTopLevelContainer(title=title, note=note, subBlocks=subBlocks)
        else:
            return

    def _handleCondition(self, name, data, uniqueName, group):
        if name == 'premium':
            return conditions.PremiumVehicle(uniqueName, data)
        if name == 'hasReceivedMultipliedXP':
            return conditions.XPMultipliedVehicle(uniqueName, data)
        if name == 'dossier':
            return conditions.VehicleDossierValue(uniqueName, data)
        if name == 'vehicleDescr':
            return conditions.VehicleDescr(uniqueName, data, self)


class PreBattleConditions(ConditionsParser):

    def __init__(self, section):
        super(PreBattleConditions, self).__init__(section, rootName='preBattle')

    def _handleCondition(self, name, data, uniqueName, group):
        if name == 'unit':
            tmpGroup = self.LOGICAL_OPS['and']()
            self._parseNode(uniqueName, data, tmpGroup)
            group.add(tmpGroup.items[0])
        else:
            if name == 'bonusTypes':
                return conditions.BattleBonusType(uniqueName, data)
            if name == 'isSquad':
                return conditions.BattleSquad(uniqueName, data)
            if name == 'clanMembership':
                return conditions.BattleClanMembership(uniqueName, data, self)
            if name == 'camouflageKind':
                return conditions.BattleCamouflage(uniqueName, data)
            if name == 'geometryNames':
                return conditions.BattleMap(uniqueName, data)

    def format(self, svrEvents, event = None):
        conds = self.getConditions()
        if not conds.isEmpty():
            return conds._formatSubBlocks(svrEvents, event)
        return []


class PostBattleConditions(ConditionsParser):

    def __init__(self, section, preBattleCond):
        self.__preBattleCond = weakref.proxy(preBattleCond)
        super(PostBattleConditions, self).__init__(section, rootName='postBattle')

    def _handleCondition(self, name, data, uniqueName, group):
        if name == 'win':
            return conditions.Win(uniqueName, data)
        if name == 'isAlive':
            return conditions.Survive(uniqueName, data)
        if name == 'achievements':
            return conditions.Achievements(uniqueName, data)
        if name == 'vehicleKills':
            return conditions.VehicleKills(uniqueName, data)
        if name == 'clanKills':
            return conditions.ClanKills(uniqueName, data)
        if name == 'results':
            return conditions.BattleResults(uniqueName, data)
        if name == 'unit':
            return conditions.UnitResults(uniqueName, data, self.__preBattleCond)
        if name == 'clubs':
            return conditions.ClubDivision(uniqueName, data)

    def format(self, svrEvents, event = None):
        conds = self.getConditions()
        if not conds.isEmpty():
            return conds._formatSubBlocks(svrEvents, event)
        return []


class BonusConditions(ConditionsParser):

    def __init__(self, section, progress, preBattleCond):
        self.__preBattleCond = weakref.proxy(preBattleCond)
        super(BonusConditions, self).__init__(section, rootName='bonusBattle')
        dictSec = dict(section)
        self._isDaily = conditions._getNodeValue(dictSec, 'daily', False)
        self._bonusLimit = conditions._getNodeValue(dictSec, 'bonusLimit')
        self._groupBy = None
        if 'groupBy' in dictSec:
            self._groupBy = conditions._getNodeValue(dict(dictSec['groupBy']), 'groupName')
        self._inRow = conditions._getNodeValue(dictSec, 'inrow', False)
        self._progress = progress
        return

    def isDaily(self):
        return self._isDaily

    def getBonusLimit(self):
        return self._bonusLimit

    def getGroupByValue(self):
        return self._groupBy

    def isInRow(self):
        return self._inRow

    def getProgress(self):
        return self._progress

    def format(self, svrEvents, event = None):
        result = []
        for c in self.getConditions().items:
            if isinstance(c, conditions._Cumulativable) and self.getGroupByValue() is None:
                fmtVal = c.formatByGroup(svrEvents, None, event)
            else:
                fmtVal = c.format(svrEvents, event)
            result.extend(fmtVal)

        return result

    def formatGroupByProgresses(self, svrEvents, event = None):
        battlesLeft = {}
        groups = defaultdict(list)
        for c in self.getConditions().items:
            if isinstance(c, conditions._Cumulativable):
                for groupByKey, (current, total, _, _) in c.getProgressPerGroup().iteritems():
                    groups[groupByKey].extend(c.formatByGroup(svrEvents, groupByKey, event))
                    if c.getName() == 'battles':
                        battlesLeft[groupByKey] = total - current

        result = []
        if event is None or not event.isCompleted():
            for groupByKey, groupConds in groups.iteritems():
                isGroupCompleted = self.__isGroupProgressCompleted(groupByKey)
                groupByItem, packedData = self.__packGroupByBlock(self.getGroupByValue(), groupByKey, battlesLeft.get(groupByKey), self.isInRow(), formatters.indexing(groupConds), isGroupCompleted)
                result.append((groupByItem, packedData, isGroupCompleted))

        def _sortFunc(a, b):
            res = int(a[2]) - int(b[2])
            if res:
                return res
            return cmp(a, b)

        return map(lambda v: v[1], sorted(result, cmp=_sortFunc))

    def _handleCondition(self, name, data, uniqueName, group):
        if name == 'battles':
            return conditions.BattlesCount(uniqueName, data, self)
        if name == 'vehicleKills':
            return conditions.VehicleKillsCumulative(uniqueName, data, self)
        if name == 'cumulative':
            result = []
            for idx, data in enumerate(data):
                result.append(conditions.CumulativeResult('%s%d' % (uniqueName, idx), (data,), self))

            return result
        if name == 'unit':
            result = []
            for idx, data in enumerate(dict(data)['cumulative']):
                result.append(conditions.CumulativeResult('%s%d' % (uniqueName, idx), (data,), self, isUnit=True, preBattleCond=self.__preBattleCond))

            return result

    def __isGroupProgressCompleted(self, groupByKey):
        progress = {}
        if self._progress is not None:
            progress = self._progress.get(groupByKey, {})
        if self._bonusLimit is not None:
            return progress.get('bonusCount', 0) >= self._bonusLimit
        else:
            return False

    @classmethod
    def __packGroupByBlock(cls, groupByValue, groupByKey, battlesLeft, inrow, conds, isGroupCompleted):
        from gui.shared import g_itemsCache
        if isGroupCompleted:
            conds = []
        if groupByValue == 'vehicle':
            vehicle = g_itemsCache.items.getItemByCD(groupByKey)
            return (vehicle, formatters.packGroupByVehicleConditions(g_itemsCache.items.getItemByCD(groupByKey), battlesLeft, inrow, conds, isCompleted=isGroupCompleted))
        if groupByValue == 'nation':
            return (GUI_NATIONS_ORDER_INDEX[groupByKey], formatters.packGroupByNationConditions(groupByKey, battlesLeft, inrow, conds, isCompleted=isGroupCompleted))
        if groupByValue == 'level':
            levelValue = int(groupByKey.replace('level ', ''))
            return (levelValue, formatters.packGroupByLevelConditions(levelValue, battlesLeft, inrow, conds, isCompleted=isGroupCompleted))
        if groupByValue == 'class':
            return (VEHICLE_TYPES_ORDER_INDICES[groupByKey], formatters.packGroupByClassConditions(groupByKey, battlesLeft, inrow, conds, isCompleted=isGroupCompleted))
