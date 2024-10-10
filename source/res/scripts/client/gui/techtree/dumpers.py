# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/techtree/dumpers.py
import gui
from account_helpers.AccountSettings import AccountSettings, EarlyAccess
from gui.techtree.techtree_dp import g_techTreeDP
from gui.techtree.settings import VehicleClassInfo, NODE_STATE
from helpers import i18n
__all__ = ('ResearchItemsObjDumper', 'StubDumper')

class _BaseDumper(object):
    __slots__ = ('_cache', '_vClassInfo')

    def __init__(self, cache=None):
        super(_BaseDumper, self).__init__()
        self._cache = cache
        self._vClassInfo = VehicleClassInfo()

    def clear(self, full=False):
        raise NotImplementedError

    def dump(self, data):
        return {}


class ResearchBaseDumper(_BaseDumper):

    def __init__(self, cache=None):
        super(ResearchBaseDumper, self).__init__(cache or self._getDefaultCacheObj())

    def clear(self, full=False):
        nodes = self._cache['nodes']
        while nodes:
            nodes.pop().clear()

        if full:
            self._vClassInfo.clear()

    def dump(self, data):
        self.clear()
        rootItem = data.getRootItem()
        cachedNodes = self._cache['nodes']
        for node in data.getNodes():
            renderer = node.getDisplayInfo().get('renderer')
            if renderer and renderer != 'vehicle':
                cachedNodes.append(self._getItemData(node, rootItem))

        return self._cache

    def _getDefaultCacheObj(self):
        return {'nodes': []}

    def _getItemData(self, node, rootItem):
        nodeCD = node.getNodeCD()
        bpProgress = 0
        if node.isVehicle():
            vClass = self._vClassInfo.getInfoByTags(node.getTags())
            bpProgress = node.getBlueprintProgress()
        else:
            vClass = {'name': node.getTypeName()}
        data = {'id': nodeCD,
         'nameString': node.getShortUserName(),
         'primaryClass': vClass,
         'level': node.getLevel(),
         'iconPath': node.getIcon(),
         'smallIconPath': node.getSmallIcon(),
         'state': node.getState(),
         'displayInfo': node.getDisplayInfo(),
         'extraInfo': node.getExtraInfo(rootItem),
         'blueprintProgress': bpProgress}
        return data


class ResearchItemsObjDumper(ResearchBaseDumper):

    def clear(self, full=False):
        nodes = self._cache['top']
        while nodes:
            nodes.pop().clear()

    def dump(self, data):
        self.clear()
        self._fillCacheSection('nodes', data, data.getNodes())
        self._fillCacheSection('top', data, data.getTopLevel())
        return self._cache

    def _fillCacheSection(self, sectionName, data, items):
        rootItem = data.getRootItem()
        self._cache[sectionName] = map(lambda node: self._getItemData(node, rootItem), items)

    def _getDefaultCacheObj(self):
        defCache = super(ResearchItemsObjDumper, self)._getDefaultCacheObj()
        defCache['top'] = []
        return defCache

    def _getExtraInfo(self, data):
        item = data.getRootItem()
        result = {}
        if item.isPremium:
            if item.isSpecial:
                tag = 'special'
            else:
                tag = 'premium'
            typeString = i18n.makeString('#tooltips:tankCaruselTooltip/vehicleType/elite/{0:>s}'.format(item.type))
            result = {'type': item.type,
             'title': gui.makeHtmlString('html_templates:lobby/research', 'premium_title', ctx={'name': item.userName,
                       'type': typeString,
                       'level': i18n.makeString('#tooltips:level/{0:d}'.format(item.level))}),
             'benefitsHead': i18n.makeString('#menu:research/{0:>s}/benefits/head'.format(tag)),
             'benefitsList': gui.makeHtmlString('html_templates:lobby/research', '{0:>s}_benefits'.format(tag), ctx={'description': item.fullDescription}),
             'isPremiumIgr': item.isPremiumIGR}
        return result

    def _getItemData(self, node, rootItem):
        data = super(ResearchItemsObjDumper, self)._getItemData(node, rootItem)
        data.update({'state': node.getState(),
         'earnedXP': node.getEarnedXP(),
         'unlockProps': node.getUnlockTuple(),
         'buyPrice': node.getBuyPrices()})
        if NODE_STATE.isEarlyAccess(node.getState()):
            data.update(_getEarlyAccessVehicleData(node))
        return data


class StubDumper(_BaseDumper):

    def clear(self, full=False):
        pass


def _getEarlyAccessVehicleData(node):
    isVehicleBlocked = node.getNodeCD() in g_techTreeDP.earlyAccessController.getBlockedVehicles()
    isBuyState = not g_techTreeDP.earlyAccessController.isAnyQuestAvailable()
    return {'isFirstTimeEarlyAccessShow': not AccountSettings.getEarlyAccess(EarlyAccess.TREE_SEEN),
     'isEarlyAccessLocked': isVehicleBlocked,
     'isEarlyAccessPaused': g_techTreeDP.earlyAccessController.isPaused(),
     'earlyAccessCurrentTokens': g_techTreeDP.earlyAccessController.getTokensBalance(),
     'earlyAccessTotalTokens': g_techTreeDP.earlyAccessController.getVehiclePrice(node.getNodeCD()),
     'isEarlyAccessCanBuy': not isVehicleBlocked and isBuyState}
