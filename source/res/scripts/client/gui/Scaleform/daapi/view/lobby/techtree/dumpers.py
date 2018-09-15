# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/dumpers.py
import gui
import nations
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.techtree import techtree_dp
from gui.Scaleform.daapi.view.lobby.techtree.settings import SelectedNation
from gui.Scaleform.daapi.view.lobby.techtree.settings import VehicleClassInfo
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.vehicle_compare.formatters import getTreeNodeCompareData, getBtnCompareData
from gui.Scaleform.locale.MENU import MENU
from gui.shared.formatters import text_styles, icons
from gui.shared.formatters.time_formatters import RentLeftFormatter
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.tooltips.formatters import packItemActionTooltipData
from gui.shared.tooltips.formatters import packItemRentActionTooltipData
from gui.shared.money import Currency
from gui.shared.tooltips.formatters import getActionPriceData
from gui.shared.utils import CLIP_ICON_PATH, HYDRAULIC_ICON_PATH
from helpers import i18n, html
__all__ = ('ResearchItemsObjDumper', 'ResearchItemsXMLDumper', 'NationObjDumper', 'NationXMLDumper')

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

    @staticmethod
    def _getVehicleStatus(item):
        status = ''
        statusLevel = ''
        if item.isRented and not item.isTelecom:
            if item.rentalIsOver:
                if item.isPremiumIGR:
                    status = i18n.makeString(MENU.CURRENTVEHICLESTATUS_IGRRENTALISOVER)
                else:
                    status = i18n.makeString(MENU.CURRENTVEHICLESTATUS_RENTALISOVER)
                statusLevel = Vehicle.VEHICLE_STATE_LEVEL.CRITICAL
            elif not item.isPremiumIGR:
                status = RentLeftFormatter(item.rentInfo).getRentLeftStr()
                statusLevel = Vehicle.VEHICLE_STATE_LEVEL.RENTED
        elif item.isRentable and item.isRentAvailable:
            status = i18n.makeString(MENU.CURRENTVEHICLESTATUS_ISRENTABLE)
            statusLevel = Vehicle.VEHICLE_STATE_LEVEL.RENTED
        elif item.canTradeIn:
            status = i18n.makeString(MENU.TRADE_IN)
            statusLevel = Vehicle.VEHICLE_STATE_LEVEL.INFO
        return (status, statusLevel)


class ResearchBaseDumper(_BaseDumper):

    def __init__(self, cache=None):
        super(ResearchBaseDumper, self).__init__(cache or self._getDefaultCacheObj())

    def _getDefaultCacheObj(self):
        return {'nodes': []}

    def clear(self, full=False):
        nodes = self._cache['nodes']
        while len(nodes):
            nodes.pop().clear()

        if full:
            self._vClassInfo.clear()

    def dump(self, data):
        self.clear()
        itemGetter = data.getItem
        rootItem = data.getRootItem()
        cachedNodes = self._cache['nodes']
        for node in data._nodes:
            renderer = node['displayInfo'].get('renderer')
            if renderer and renderer != 'vehicle':
                cachedNodes.append(self._getItemData(node, itemGetter(node['id']), rootItem))

        return self._cache

    def _getItemData(self, node, item, rootItem):
        nodeCD = node['id']
        vClass = {'name': ''}
        extraInfo = None
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            vClass = self._vClassInfo.getInfoByTags(item.tags)
        else:
            if item.itemTypeID == GUI_ITEM_TYPE.GUN and item.isClipGun(rootItem.descriptor):
                extraInfo = CLIP_ICON_PATH
            elif item.itemTypeID == GUI_ITEM_TYPE.CHASSIS and item.isHydraulicChassis():
                extraInfo = HYDRAULIC_ICON_PATH
            vClass.update({'name': item.itemTypeName})
        data = {'id': nodeCD,
         'nameString': item.shortUserName,
         'primaryClass': vClass,
         'level': item.level,
         'iconPath': item.icon,
         'state': node['state'],
         'displayInfo': node['displayInfo'],
         'extraInfo': extraInfo}
        return data


class ResearchItemsObjDumper(ResearchBaseDumper):
    """
    Converts data of research items for given vehicle to list of objects.
    """

    def clear(self, full=False):
        nodes = self._cache['top']
        while len(nodes):
            nodes.pop().clear()

        self._cache['global']['extraInfo'].clear()

    def dump(self, data):
        self.clear()
        self._fillCacheSection('nodes', data, data._nodes)
        self._fillCacheSection('top', data, data._topLevel)
        self._getGlobalData(data)
        return self._cache

    def _fillCacheSection(self, sectionName, data, items):
        itemGetter = data.getItem
        rootItem = data.getRootItem()
        self._cache[sectionName] = map(lambda node: self._getItemData(node, itemGetter(node['id']), rootItem), items)

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

    def _getItemData(self, node, item, rootItem):
        nodeCD = node['id']
        vClass = {'name': ''}
        status = statusLevel = ''
        vehicleBtnLabel = ''
        if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            status, statusLevel = self._getVehicleStatus(item)
            if item.isInInventory:
                vehicleBtnLabel = MENU.RESEARCH_LABELS_BUTTON_SHOWINHANGAR
            else:
                vehicleBtnLabel = MENU.RESEARCH_SHOWINPREVIEWBTN_LABEL
        else:
            vClass.update({'name': item.itemTypeName})
        price = node['GUIPrice']
        data = {'longName': item.longUserName,
         'smallIconPath': item.iconSmall,
         'earnedXP': node['earnedXP'],
         'shopPrice': (price.getSignValue(Currency.CREDITS), price.getSignValue(Currency.GOLD), getActionPriceData(item)),
         'unlockProps': node['unlockProps']._makeTuple(),
         'status': status,
         'statusLevel': statusLevel,
         'isPremiumIGR': item.isPremiumIGR,
         'showVehicleBtnLabel': i18n.makeString(vehicleBtnLabel),
         'showVehicleBtnEnabled': item.isInInventory or item.isPreviewAllowed(),
         'vehCompareRootData': getBtnCompareData(item) if nodeCD == rootItem.intCD else {},
         'vehCompareTreeNodeData': getTreeNodeCompareData(item) if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE else {}}
        commonData = super(ResearchItemsObjDumper, self)._getItemData(node, item, rootItem)
        data.update(commonData)
        return data


class ResearchItemsXMLDumper(ResearchItemsObjDumper):
    __xmlBody = '<?xml version="1.0" encoding="utf-8"?><graph><top>{0:>s}</top><nodes>{1:>s}</nodes><global><enableInstallItems>{2[enableInstallItems]:b}</enableInstallItems><statusString>{2[statusString]:>s}</statusString><extraInfo><type>{2[extraInfo][type]:>s}</type><title><![CDATA[{2[extraInfo][title]:>s}]]></title><benefitsHead><![CDATA[{2[extraInfo][benefitsHead]:>s}]]></benefitsHead><benefitsList><![CDATA[{2[extraInfo][benefitsList]:>s}]]></benefitsList></extraInfo><freeXP>{2[freeXP]:n}</freeXP><hasNationTree>{2[hasNationTree]:b}</hasNationTree></global></graph>'
    __nodeFormat = '<node><id>{id:d}</id><nameString>{nameString:>s}</nameString><class><name>{primaryClass[name]:>s}</name></class><level>{level:d}</level><earnedXP>{earnedXP:d}</earnedXP><state>{state:d}</state><unlockProps><parentID>{unlockProps[0]:d}</parentID><unlockIdx>{unlockProps[1]:d}</unlockIdx><xpCost>{unlockProps[2]:n}</xpCost><required>{unlockProps[3]:>s}</required></unlockProps><smallIconPath><![CDATA[{smallIconPath:>s}]]></smallIconPath><iconPath><![CDATA[{iconPath:>s}]]></iconPath><longName>{longName:>s}</longName><shopPrice><credits>{shopPrice[0]:n}</credits><gold>{shopPrice[1]:n}</gold></shopPrice><display><renderer>{displayInfo[renderer]:>s}</renderer><path>{displayInfo[path]:>s}</path><level>{displayInfo[level]:d}</level></display></node>'
    __idFormat = '<id>{0:d}</id>'

    def __init__(self):
        super(ResearchItemsXMLDumper, self).__init__('')

    def clear(self, full=False):
        self._cache = ''

    def dump(self, data):
        self._cache = self.__xmlBody.format(self.__buildNodesData(data, '_topLevel'), self.__buildNodesData(data, '_nodes'), self._getGlobalData(data))
        return self._cache

    def _getExtraInfo(self, data):
        result = super(ResearchItemsXMLDumper, self)._getExtraInfo(data)
        return {'type': result.get('type', ''),
         'title': html.escape(result.get('title', '')),
         'content': html.escape(result.get('content', ''))}

    def __buildNodesData(self, data, storage):
        nodesDump = []
        itemGetter = data.getItem
        nodes = getattr(data, storage, [])
        for node in nodes:
            data = self._getItemData(node, itemGetter(node['id']), data.getRootCD())
            data['unlockProps'] = self.__buildUnlockProps(data['unlockProps'])
            data['displayInfo'] = self.__buildDisplayInfo(data['displayInfo'])
            nodesDump.append(self.__nodeFormat.format(**data))

        return ''.join(nodesDump)

    def __buildUnlockProps(self, unlockProps):
        dump = map(lambda item: self.__idFormat.format(item), unlockProps[-1])
        return unlockProps[:-1] + (''.join(dump),)

    def __buildDisplayInfo(self, displayInfo):
        info = displayInfo.copy()
        info['path'] = ''.join(map(lambda item: self.__idFormat.format(item), displayInfo['path']))
        return info


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
        while len(nodes):
            nodes.pop().clear()

        if full:
            self._vClassInfo.clear()
            self._cache['displaySettings'].clear()

    def dump(self, data):
        self.clear()
        nodes = data._nodes
        itemGetter = data.getItem
        self._cache['nodes'] = map(lambda node: self._getVehicleData(node, itemGetter(node['id'])), nodes)
        self._cache['scrollIndex'] = data._scrollIndex
        self._cache['displaySettings'].update(g_techTreeDP.getDisplaySettings(SelectedNation.getIndex()))
        return self._cache

    def _getVehicleData(self, node, item):
        nodeCD = node['id']
        tags = item.tags
        price = node['GUIPrice']
        status, statusLevel = self._getVehicleStatus(item)
        return {'id': nodeCD,
         'state': node['state'],
         'type': item.itemTypeName,
         'nameString': item.shortUserName,
         'primaryClass': self._vClassInfo.getInfoByTags(tags),
         'level': item.level,
         'longName': item.longUserName,
         'iconPath': item.icon,
         'smallIconPath': item.iconSmall,
         'earnedXP': node['earnedXP'],
         'shopPrice': (price.getSignValue(Currency.CREDITS), price.getSignValue(Currency.GOLD), getActionPriceData(item)),
         'displayInfo': node['displayInfo'],
         'unlockProps': node['unlockProps']._makeTuple(),
         'status': status,
         'statusLevel': statusLevel,
         'isRemovable': item.isRented,
         'isPremiumIGR': item.isPremiumIGR,
         'vehCompareTreeNodeData': getTreeNodeCompareData(item)}


class NationXMLDumper(NationObjDumper):
    """
    Converts data of given nation tree to xml string. Using in development version.
    """
    __xmlBody = '<?xml version="1.0" encoding="utf-8"?><tree><nodes>{0:>s}</nodes><scrollIndex>{1:d}</scrollIndex></tree>'
    __nodeFormat = '<node><id>{id:d}</id><nameString>{nameString:>s}</nameString><class><name>{primaryClass[name]:>s}</name></class><level>{level:d}</level><earnedXP>{earnedXP:d}</earnedXP><state>{state:d}</state><unlockProps><parentID>{unlockProps[0]:d}</parentID><unlockIdx>{unlockProps[1]:d}</unlockIdx><xpCost>{unlockProps[2]:n}</xpCost><topIDs>{unlockProps[3]:>s}</topIDs></unlockProps><iconPath>{iconPath:>s}</iconPath><smallIconPath><![CDATA[{smallIconPath:>s}]]></smallIconPath><longName>{longName:>s}</longName><shopPrice><credits>{shopPrice[0]:n}</credits><gold>{shopPrice[1]:n}</gold></shopPrice><display>{displayInfo:>s}</display></node>'
    __displayInfoFormat = '<row>{row:d}</row><column>{column:d}</column><position><x>{position[0]:n}</x><y>{position[1]:n}</y></position><lines>{lines:>s}</lines>'
    __setFormat = '<set><outLiteral>{0:>s}</outLiteral><outPin><x>{1[0]:n}</x><y>{1[1]:n}</y></outPin><inPins>{2:>s}</inPins></set>'
    __inPinFormat = '<item><childID>{childID:d}</childID><inPin><x>{inPin[0]:n}</x><y>{inPin[1]:n}</y></inPin><viaPins>{dump:>s}</viaPins></item>'
    __viaPinFormat = '<pin><x>{0[0]:n}</x><y>{0[1]:n}</y></pin>'
    __topIDFormat = '<id>{0:d}</id>'

    def __init__(self):
        super(NationXMLDumper, self).__init__('')

    def clear(self, full=False):
        self._cache = ''

    def dump(self, data):
        self._cache = self.__xmlBody.format(self.__buildNodesData(data), data._scrollIndex)
        return self._cache

    def __buildNodesData(self, data):
        nodesDump = []
        itemGetter = data.getItem
        for node in data._nodes:
            data = self._getVehicleData(node, itemGetter(node['id']))
            data['unlockProps'] = self.__buildUnlockProps(data['unlockProps'])
            data['displayInfo'] = self.__buildDisplayInfo(data['displayInfo'])
            nodesDump.append(self.__nodeFormat.format(**data))

        return ''.join(nodesDump)

    def __buildUnlockProps(self, unlockProps):
        dump = map(lambda item: self.__topIDFormat.format(item), unlockProps[-1])
        return unlockProps[:-1] + (''.join(dump),)

    def __buildDisplayInfo(self, displayInfo):
        info = displayInfo.copy()
        lines = info['lines']
        dump = []
        for data in lines:
            inPins = []
            for inPin in data['inPins']:
                viaPins = map(lambda item: self.__viaPinFormat.format(item), inPin['viaPins'])
                inPins.append(self.__inPinFormat.format(dump=''.join(viaPins), **inPin))

            dump.append(self.__setFormat.format(data['outLiteral'], data['outPin'], ''.join(inPins)))

        info['lines'] = ''.join(dump)
        return self.__displayInfoFormat.format(**info)
