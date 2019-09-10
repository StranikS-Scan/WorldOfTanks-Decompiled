# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/dumpers.py
import gui
from gui.Scaleform.daapi.view.lobby.techtree.settings import SelectedNation
from gui.Scaleform.daapi.view.lobby.techtree.settings import VehicleClassInfo
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
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
        if node.isVehicle():
            vClass = self._vClassInfo.getInfoByTags(node.getTags())
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
         'extraInfo': node.getExtraInfo(rootItem)}
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
        return data


class NationObjDumper(_BaseDumper):

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
        self._cache['nodes'] = map(self._getVehicleData, data.getNodes())
        self._cache['scrollIndex'] = data._scrollIndex
        self._cache['displaySettings'].update(g_techTreeDP.getDisplaySettings(SelectedNation.getIndex()))
        return self._cache

    def _getVehicleData(self, node):
        tags = node.getTags()
        blueprints = node.getBpfProps()
        return {'id': node.getNodeCD(),
         'state': node.getState(),
         'type': node.getTypeName(),
         'nameString': node.getShortUserName(),
         'primaryClass': self._vClassInfo.getInfoByTags(tags),
         'level': node.getLevel(),
         'smallIconPath': node.getSmallIcon(),
         'earnedXP': node.getEarnedXP(),
         'displayInfo': node.getDisplayInfo(),
         'unlockProps': node.getUnlockTuple(),
         'isRemovable': node.isRented(),
         'vehCompareTreeNodeData': node.getCompareData(),
         'blueprintLabel': node.getBlueprintLabel(),
         'blueprintProgress': node.getBlueprintProgress(),
         'blueprintCanConvert': blueprints.canConvert if blueprints is not None else False,
         'buyPrice': node.getBuyPrices(),
         'isNationChangeAvailable': node.hasItemNationGroup()}
