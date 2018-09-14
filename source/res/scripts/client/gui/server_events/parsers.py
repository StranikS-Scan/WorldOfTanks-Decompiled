# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/parsers.py
import weakref
from gui.server_events import formatters, conditions
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class ConditionsParser(object):
    LOGICAL_OPS = {'and': conditions.AndGroup,
     'or': conditions.OrGroup}
    NEGATIVE_OP = 'not'

    def __init__(self, section, rootName=''):
        self._section = section
        self._rootNode = None
        self.__rootName = rootName
        return

    def getConditions(self):
        if self._rootNode is None:
            self._rootNode = self._parse()
        return self._rootNode

    def getSection(self):
        return self._section

    def clearCache(self):
        self._rootNode = None
        return

    def forEachNodeInTree(self, handler):
        assert handler is not None
        self.__forEachNode(self.getConditions(), handler)
        return

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

    def _parseNode(self, uniquePath, section, group, isNegative=False):
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
                handler(node)

            return


class AccountRequirements(ConditionsParser):

    def __init__(self, section):
        super(AccountRequirements, self).__init__(section, rootName='account')
        self._hasIgrCondition = False

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
        return conditions.RefSystemRalBought10Lvl(uniqueName, data) if name == 'refSystemRalBought10Lvl' else None

    def isAvailable(self):
        conds = self.getConditions()
        return conds.isAvailable() if not conds.isEmpty() else True

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


class TokenQuestAccountRequirements(AccountRequirements):
    """ Account requirements of TokenQuest
    
    We need a special token conditions that acts like a regular one but
    is always available (see WOTD-81694). Other than that they work the same.
    """

    def _handleCondition(self, name, data, uniqueName, group):
        return conditions.TokenQuestToken(uniqueName, data) if name == 'token' else super(TokenQuestAccountRequirements, self)._handleCondition(name, data, uniqueName, group)


class VehicleRequirements(ConditionsParser):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, section):
        super(VehicleRequirements, self).__init__(section, rootName='vehicle')
        self._suitableVehicles = []

    def clearItemsCache(self):
        self._suitableVehicles = []
        self.forEachNodeInTree(lambda node: node.clearItemsCache())

    def isAvailable(self, vehicle):
        conds = self.getConditions()
        return conds.isAvailable(vehicle) if not conds.isEmpty() else True

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
        if self._suitableVehicles:
            return self._suitableVehicles
        invVehs = self.itemsCache.items.inventory.getItems(GUI_ITEM_TYPE.VEHICLE) or {}
        vehGetter = self.itemsCache.items.getVehicle
        suitableVehiclesAppend = self._suitableVehicles.append
        isAvailable = self.isAvailable
        for invID in invVehs.iterkeys():
            vehicleItem = vehGetter(invID)
            if isAvailable(vehicleItem):
                suitableVehiclesAppend(vehicleItem)

        return self._suitableVehicles

    def _handleCondition(self, name, data, uniqueName, group):
        if name == 'premium':
            return conditions.PremiumVehicle(uniqueName, data)
        if name == 'hasReceivedMultipliedXP':
            return conditions.XPMultipliedVehicle(uniqueName, data)
        return conditions.VehicleDescr(uniqueName, data) if name == 'vehicleDescr' else None


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
            if name == 'mapCamouflageKind':
                return conditions.BattleCamouflage(uniqueName, data)
            if name == 'geometryNames':
                return conditions.BattleMap(uniqueName, data)


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
        if name == 'vehicleDamage':
            return conditions.VehicleDamage(uniqueName, data)
        if name == 'clanKills':
            return conditions.ClanKills(uniqueName, data)
        if name == 'results':
            return conditions.BattleResults(uniqueName, data)
        return conditions.UnitResults(uniqueName, data, self.__preBattleCond) if name == 'unit' else None


class BonusConditions(ConditionsParser):
    itemsCache = dependency.descriptor(IItemsCache)

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

    def _handleCondition(self, name, data, uniqueName, group):
        if name == 'battles':
            return conditions.BattlesCount(uniqueName, data, self)
        if name == 'vehicleKills':
            return conditions.VehicleKillsCumulative(uniqueName, data, self)
        if name == 'vehicleDamage':
            return conditions.VehicleDamageCumulative(uniqueName, data, self)
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

    def isGroupProgressCompleted(self, groupByKey):
        progress = {}
        if self._progress is not None:
            progress = self._progress.get(groupByKey, {})
        return progress.get('bonusCount', 0) >= self._bonusLimit if self._bonusLimit is not None else False
