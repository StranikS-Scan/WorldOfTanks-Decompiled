# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/dumpers.py
import gui
import nations
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.techtree import techtree_dp
from gui.Scaleform.daapi.view.lobby.techtree.settings import SelectedNation
from gui.Scaleform.daapi.view.lobby.techtree.settings import VehicleClassInfo
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.vehicle_compare import formatters as vc_formatters
from helpers import i18n
__all__ = ('ResearchItemsObjDumper', 'NationObjDumper')

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

    def _getDefaultCacheObj(self):
        return {'nodes': []}

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

    def _getItemData(self, node, rootItem):
        nodeCD = node.getNodeCD()
        if node.isVehicle():
            vClass = self._vClassInfo.getInfoByTags(node.getTags())
        else:
            vClass = {'name': node.getTypeName()}
        data = {'id': nodeCD,
         'nameString': node.getShortUserName(),
         'primaryClass': vClass,
         'level': node.getLevel(),
         'iconPath': node.getIcon(),
         'state': node.getState(),
         'displayInfo': node.getDisplayInfo(),
         'extraInfo': node.getExtraInfo(rootItem)}
        return data


class ResearchItemsObjDumper(ResearchBaseDumper):
    """
    Converts data of research items for given vehicle to list of objects.
    """

    def clear(self, full=False):
        nodes = self._cache['top']
        while nodes:
            nodes.pop().clear()

        self._cache['global']['extraInfo'].clear()

    def dump(self, data):
        self.clear()
        self._fillCacheSection('nodes', data, data.getNodes())
        self._fillCacheSection('top', data, data.getTopLevel())
        self._getGlobalData(data)
        return self._cache

    def _fillCacheSection(self, sectionName, data, items):
        rootItem = data.getRootItem()
        self._cache[sectionName] = map(lambda node: self._getItemData(node, rootItem), items)

    def _getDefaultCacheObj(self):
        defCache = super(ResearchItemsObjDumper, self)._getDefaultCacheObj()
        defCache['top'] = []
        defCache['global'] = {'enableInstallItems': False,
         'statusString': None,
         'extraInfo': {},
         'freeXP': 0,
         'hasNationTree': False}
        return defCache

    def _getGlobalData(self, data):
        try:
            nation = nations.NAMES[data.getNationID()]
        except IndexError:
            LOG_ERROR('Nation not found', data.getNationID())
            nation = None

        globalData = self._cache['global']
        warningMessage = None
        globalData.update({'enableInstallItems': data.isInstallItemsEnabled(),
         'statusString': data.getRootStatusString(),
         'extraInfo': self._getExtraInfo(data),
         'freeXP': data.getUnlockStats().freeXP,
         'hasNationTree': nation in techtree_dp.g_techTreeDP.getAvailableNations(),
         'warningMessage': warningMessage,
         'historicalBattleID': -1})
        return

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
        nodeCD = node.getNodeCD()
        status = statusLevel = node.getStatus()
        data = {'longName': node.getLongUserName(),
         'smallIconPath': node.getSmallIcon(),
         'earnedXP': node.getEarnedXP(),
         'shopPrice': node.getShopPrice(),
         'unlockProps': node.getUnlockTuple(),
         'status': status,
         'statusLevel': statusLevel,
         'isPremiumIGR': node.isPremiumIGR(),
         'showVehicleBtnLabel': node.getPreviewLabel(),
         'showVehicleBtnEnabled': node.isPreviewAllowed(),
         'vehCompareRootData': vc_formatters.getBtnCompareData(rootItem) if nodeCD == rootItem.intCD else {},
         'vehCompareTreeNodeData': node.getCompareData()}
        commonData = super(ResearchItemsObjDumper, self)._getItemData(node, rootItem)
        data.update(commonData)
        return data


class NationObjDumper(_BaseDumper):
    """
    Converts data of nation tree to list of objects.
    """

    def __init__(self, cache=None):
        if cache is None:
            cache = {'nodes': [],
             'displaySettings': {},
             'scrollIndex': -1}
        super(NationObjDumper, self).__init__(cache)
        return

    def clear(self, full=False):
        nodes = self._cache['nodes']
        while nodes:
            nodes.pop().clear()

        if full:
            self._vClassInfo.clear()
            self._cache['displaySettings'].clear()

    def dump(self, data):
        self.clear()
        self._cache['nodes'] = map(lambda node: self._getVehicleData(node), data.getNodes())
        self._cache['scrollIndex'] = data._scrollIndex
        self._cache['displaySettings'].update(g_techTreeDP.getDisplaySettings(SelectedNation.getIndex()))
        return self._cache

    def _getVehicleData(self, node):
        tags = node.getTags()
        status, statusLevel = node.getStatus()
        return {'id': node.getNodeCD(),
         'state': node.getState(),
         'type': node.getTypeName(),
         'nameString': node.getShortUserName(),
         'primaryClass': self._vClassInfo.getInfoByTags(tags),
         'level': node.getLevel(),
         'longName': node.getLongUserName(),
         'iconPath': node.getIcon(),
         'smallIconPath': node.getSmallIcon(),
         'earnedXP': node.getEarnedXP(),
         'shopPrice': node.getShopPrice(),
         'displayInfo': node.getDisplayInfo(),
         'unlockProps': node.getUnlockTuple(),
         'status': status,
         'statusLevel': statusLevel,
         'isRemovable': node.isRented(),
         'isPremiumIGR': node.isPremiumIGR(),
         'vehCompareTreeNodeData': node.getCompareData()}
