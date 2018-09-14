# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/data_providers.py
import cPickle
import constants
import gui
import Math
import time
import Event
from abc import abstractmethod, ABCMeta
from debug_utils import LOG_WARNING, LOG_DEBUG
from gui.Scaleform.daapi.view.lobby.customization.VehicleCustonizationModel import VehicleCustomizationModel
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule
from gui.Scaleform.genConsts.CUSTOMIZATION_ITEM_TYPE import CUSTOMIZATION_ITEM_TYPE
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE, ACTION_TOOLTIPS_STATE
from items import vehicles
from items.vehicles import CAMOUFLAGE_KINDS
from helpers import i18n
from CurrentVehicle import g_currentVehicle
from gui.ClientHangarSpace import _CAMOUFLAGE_MIN_INTENSITY
from gui.Scaleform.framework.entities.DAAPIDataProvider import DAAPIDataProvider
from gui.shared import g_itemsCache
from gui.shared.utils.functions import makeTooltip
from gui import g_tankActiveCamouflage
from gui.Scaleform.daapi.view.lobby.customization import CustomizationHelper

class BaseCustomizationDataProvider(BaseDAAPIModule):

    def __init__(self, nationID):
        super(BaseCustomizationDataProvider, self).__init__()
        self.nationID = nationID
        self._defCost = -1.0
        self._cost = -1.0
        self._period = -1.0
        self._isIGR = False
        self._isGold = 0
        self._vehPriceFactor = 1.0
        self._defVehPriceFactor = 1.0
        self.currentItemID = None
        self._currentType = None
        return

    @classmethod
    def _makeCost(cls, defCost, vehPriceFactor, priceFactor):
        return int(round(defCost * vehPriceFactor * priceFactor))

    def _getPriceFactor(self, itemID):
        LOG_WARNING('Method must be overridden!')

    def getCost(self, itemID):
        return (self._makeCost(self._cost, self._vehPriceFactor, self._getPriceFactor(itemID)), self._isGold)

    def setDefaultCost(self, cost, defCost, isGold, isIGR, period):
        self._cost = cost
        self._defCost = defCost
        self._isGold = isGold == 1
        self._isIGR = isIGR
        self._period = period

    def refresh(self):
        self.flashObject.invalidateRemote(True)

    def isNewID(self, itemID):
        return CustomizationHelper.checkIsNewItem(self._currentType, itemID, self.nationID)

    def _hasNewItems(self, type, itemsInGroupIDs):
        newItemsIds = CustomizationHelper.getNewIdsByType(type, self.nationID)
        if type == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE:
            groupIdsSet = set(itemsInGroupIDs)
        else:
            groupIdsSet = set(((self.nationID, id) for id in itemsInGroupIDs))
        result = groupIdsSet.intersection(newItemsIds)
        return len(result) > 0


class BaseGroupsDataProvider(DAAPIDataProvider):

    def __init__(self, nationID):
        super(BaseGroupsDataProvider, self).__init__()
        self._list = []
        self._nationID = nationID

    @property
    def collection(self):
        return self._list

    def _hasNewItems(self, type, itemsInGroupIDs):
        newItemsIds = CustomizationHelper.getNewIdsByType(type, self._nationID)
        if type == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE:
            groupIdsSet = set(itemsInGroupIDs)
        else:
            groupIdsSet = set(((self._nationID, id) for id in itemsInGroupIDs))
        result = groupIdsSet.intersection(newItemsIds)
        return len(result) > 0


class CamouflageGroupsDataProvider(BaseGroupsDataProvider):

    def __init__(self, nationID):
        super(CamouflageGroupsDataProvider, self).__init__(nationID)

    def buildList(self):
        customization = vehicles.g_cache.customization(self._nationID)
        result = []
        compactDescr = g_currentVehicle.item.descriptor.type.compactDescr
        activeGroup = g_tankActiveCamouflage['historical'].get(compactDescr)
        if activeGroup is None:
            activeGroup = g_tankActiveCamouflage.get(compactDescr, 0)
        if customization is not None:
            groups = customization.get('camouflageGroups', {})
            for name, info in groups.iteritems():
                isHasNew = self._hasNewItems(CUSTOMIZATION_ITEM_TYPE.CAMOUFLAGE_TYPE, info.get('ids', []))
                if name in CAMOUFLAGE_KINDS:
                    groupId = CAMOUFLAGE_KINDS.get(name)
                    result.append({'name': name,
                     'userString': info.get('userString', name),
                     'hasNew': isHasNew,
                     'kind': groupId,
                     'enabled': True,
                     'selected': activeGroup == groupId})

        self._list = sorted(result, cmp=self.__comparator)
        return

    def emptyItem(self):
        return {'name': None,
         'userString': '',
         'hasNew': False,
         'kind': -1,
         'enabled': False}

    def __comparator(self, item, other):
        return cmp(item.get('kind'), other.get('kind'))


class HornsDataProvider(DAAPIDataProvider):

    def __init__(self):
        super(HornsDataProvider, self).__init__()
        self.__vehicleTags = set()
        self.__list = []

    def buildList(self, currentHornID):
        horns = vehicles.g_cache.horns()
        result = []
        if horns is not None:
            for id, info in horns.iteritems():
                allowedTags = info.get('vehicleTags', set())
                if self.__vehicleTags & allowedTags:
                    result.append({'id': id,
                     'userString': info.get('userString', ''),
                     'gold': self.getCost(id),
                     'current': currentHornID == id})

        self.__list = sorted(result, cmp=lambda item, other: cmp(item.get('userString'), other.get('userString')))
        return

    def emptyItem(self):
        return {'id': None,
         'userString': '',
         'gold': 0,
         'current': False}

    @classmethod
    def _makeCost(cls, defCost, priceFactor):
        return int(round(defCost * priceFactor))

    def getCost(self, hornID):
        price = g_itemsCache.items.shop.getHornPrice(hornID)
        return self._makeCost(price, g_itemsCache.items.shop.getHornPriceFactor())

    def makeItem(self, hornID, isCurrent):
        horn = vehicles.g_cache.horns().get(hornID, {})
        return {'id': hornID,
         'userString': horn.get('userString', ''),
         'gold': self.getCost(hornID),
         'current': isCurrent}

    def setVehicleTypeParams(self, vehicleTags, defaultVehicleTags, hornPriceFactor):
        self.__vehicleTags = vehicleTags

    def setHornDefCosts(self, costs):
        pass

    @property
    def collection(self):
        return self.__list


class RentalPackageDataProviderBase(DAAPIDataProvider):
    __metaclass__ = ABCMeta
    DEFAULT_RENTAL_PACKAGE_IDX = 0

    def __init__(self, nationID):
        super(RentalPackageDataProviderBase, self).__init__()
        self._list = []
        self._items = None
        self._defaultItems = None
        self._selectedPackageIndex = self.DEFAULT_RENTAL_PACKAGE_IDX
        self._eventManager = Event.EventManager()
        self.onDataInited = Event.Event(self._eventManager)
        self.onRentalPackageChange = Event.Event(self._eventManager)
        self.nationID = nationID
        return

    @abstractmethod
    def getRentalPackages(self, refresh = False):
        pass

    def __getSelectedPackageIndex(self):
        return self._selectedPackageIndex

    def __setSelectedPackageIndex(self, value):
        self._selectedPackageIndex = value
        self.onRentalPackageChange(self.selectedPackageIndex)

    selectedPackageIndex = property(__getSelectedPackageIndex, __setSelectedPackageIndex)
    selectedPackage = property(lambda self: self.pyRequestItemAt(self._selectedPackageIndex))

    def getIndexByDays(self, days, isIGR):
        findIdx = self.DEFAULT_RENTAL_PACKAGE_IDX
        for idx, item in enumerate(self._list):
            if item.get('periodDays') == days and item.get('isIGR') == isIGR:
                findIdx = idx
                break

        return findIdx

    def emptyItem(self):
        return {'periodDays': -1,
         'cost': -1,
         'isGold': False,
         'userString': '',
         'isIGR': False,
         'enabled': False}

    @property
    def collection(self):
        return self._list

    def _onGetPackagesCost(self, costs, defaultCosts, refresh):
        self.buildList(costs, defaultCosts)
        self.onDataInited(self.selectedPackage, refresh)

    def refreshList(self):
        self.buildList(self._items, self._defaultItems)

    def buildList(self, costs, defaultCosts):
        items = {}
        if costs is not None:
            items = costs.copy()
        defaultItems = {}
        if defaultCosts is not None:
            defaultItems = defaultCosts.copy()
        self._items = items
        self._defaultItems = defaultItems
        result = []
        nations = {}
        if items.has_key('nations'):
            nations = items.get('nations', {})
            del items['nations']
        if nations.has_key(self.nationID):
            items.update(nations.get(self.nationID))
        for periodDays, (cost, isGold) in items.iteritems():
            if periodDays > 1:
                i18nPeriodDays = i18n.makeString(MENU.CUSTOMIZATION_PERIOD_DAYS, periodDays)
            elif periodDays == 1:
                i18nPeriodDays = i18n.makeString(MENU.CUSTOMIZATION_PERIOD_DAY)
            else:
                i18nPeriodDays = i18n.makeString(MENU.CUSTOMIZATION_PERIOD_INFINITY)
            result.append({'periodDays': periodDays,
             'cost': cost,
             'defCost': defaultCosts.get(periodDays, (0, 1))[0],
             'isGold': isGold == 1,
             'userString': i18nPeriodDays,
             'isIGR': False,
             'enabled': True})

        self._list = sorted(result, cmp=self._comparator, reverse=True)
        return

    def _comparator(self, item, other):
        result = 0
        if item.get('periodDays') and other.get('periodDays') and item.get('periodDays') != other.get('periodDays'):
            result = cmp(item.get('periodDays'), other.get('periodDays'))
        elif not item.get('periodDays') and not other.get('periodDays'):
            result = 1 if item.get('isIGR') else -1
        elif item.get('periodDays') != other.get('periodDays'):
            result = 1 if not item.get('periodDays') else -1
        return result

    def getSelectedPackageIndex(self):
        return self.selectedPackageIndex

    def setSelectedPackageIndex(self, value):
        self.selectedPackageIndex = value


class CamouflageRentalPackageDataProvider(RentalPackageDataProviderBase):

    def getRentalPackages(self, refresh = False):
        costs = g_itemsCache.items.shop.camouflageCost
        defaultCosts = g_itemsCache.items.shop.defaults.camouflageCost
        self._onGetPackagesCost(costs, defaultCosts, refresh)

    def buildList(self, costs, defaultCosts):
        RentalPackageDataProviderBase.buildList(self, costs, defaultCosts)
        if gui.GUI_SETTINGS.igrEnabled:
            igrRoomType = gui.game_control.g_instance.igr.getRoomType()
            icon = gui.makeHtmlString('html_templates:igr/iconSmall', 'premium')
            self._list.append({'periodDays': 0,
             'cost': 0,
             'defCost': 0,
             'isGold': 1,
             'userString': i18n.makeString(MENU.CUSTOMIZATION_PERIOD_IGR, igrImg=icon),
             'isIGR': True,
             'enabled': igrRoomType == constants.IGR_TYPE.PREMIUM})
            if igrRoomType != constants.IGR_TYPE.PREMIUM:
                self._selectedPackageIndex = 1
        self._list = sorted(self._list, cmp=self._comparator, reverse=True)


class EmblemRentalPackageDataProvider(RentalPackageDataProviderBase):

    def getRentalPackages(self, refresh = False):
        costs = g_itemsCache.items.shop.playerEmblemCost
        defaultCosts = g_itemsCache.items.shop.defaults.playerEmblemCost
        self._onGetPackagesCost(costs, defaultCosts, refresh)


class InscriptionRentalPackageDataProvider(RentalPackageDataProviderBase):

    def getRentalPackages(self, refresh = False):
        costs = g_itemsCache.items.shop.playerInscriptionCost
        defaultCosts = g_itemsCache.items.shop.defaults.playerInscriptionCost
        self._onGetPackagesCost(costs, defaultCosts, refresh)


class InscriptionGroupsDataProvider(BaseGroupsDataProvider):

    def __init__(self, nationID):
        super(InscriptionGroupsDataProvider, self).__init__(nationID)

    def buildList(self):
        hiddenInscriptions = g_itemsCache.items.shop.getInscriptionsGroupHiddens(self._nationID)
        customization = vehicles.g_cache.customization(self._nationID)
        result = []
        if customization is not None:
            igrRoomType = gui.game_control.g_instance.igr.getRoomType()
            groups = customization.get('inscriptionGroups', {})
            for name, group in groups.iteritems():
                inscriptionIDs, groupUserString, igrType, allow, deny = group
                isHasNew = self._hasNewItems(CUSTOMIZATION_ITEM_TYPE.INSCRIPTION_TYPE, inscriptionIDs)
                isHiddenGroup = name in hiddenInscriptions
                currVehIntD = g_currentVehicle.item.intCD
                canBeUsedOnVehicle = currVehIntD not in deny and (len(allow) == 0 or currVehIntD in allow)
                hasItemsInHangar = False
                if isHiddenGroup:
                    hasItemsInHangar = CustomizationHelper.areItemsInHangar(CUSTOMIZATION_ITEM_TYPE.INSCRIPTION, inscriptionIDs, self._nationID)
                if canBeUsedOnVehicle and (isHasNew or hasItemsInHangar or not isHiddenGroup) and (gui.GUI_SETTINGS.igrEnabled or not gui.GUI_SETTINGS.igrEnabled and igrType == constants.IGR_TYPE.NONE):
                    result.append({'name': name,
                     'userString': groupUserString,
                     'hasNew': isHasNew,
                     'isIGR': igrType != constants.IGR_TYPE.NONE,
                     'enabled': igrType == constants.IGR_TYPE.NONE or igrType <= igrRoomType,
                     'tooltip': TOOLTIPS.CUSTOMIZATION_INSCRIPTION_IGR})

        self._list = sorted(result, cmp=self.__comparator)
        return

    def emptyItem(self):
        return {'name': None,
         'userString': '',
         'hasNew': False,
         'isIGR': False,
         'enabled': False}

    def __comparator(self, item, other):
        if item.get('isIGR') == other.get('isIGR'):
            return cmp(item.get('name'), other.get('name'))
        elif item.get('isIGR'):
            return -1
        else:
            return 1


class EmblemGroupsDataProvider(BaseGroupsDataProvider):

    def __init__(self, nationID):
        super(EmblemGroupsDataProvider, self).__init__(nationID)

    def buildList(self):
        hiddenEmblems = g_itemsCache.items.shop.getEmblemsGroupHiddens()
        groups, emblems, names = vehicles.g_cache.playerEmblems()
        result = []
        if groups is not None:
            igrRoomType = gui.game_control.g_instance.igr.getRoomType()
            for name, group in groups.iteritems():
                emblemIDs, groupUserString, igrType, nations, allow, deny = group
                isHasNew = self._hasNewItems(CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE, emblemIDs)
                isHiddenGroup = name in hiddenEmblems
                hasItemsInHangar = False
                currVehIntD = g_currentVehicle.item.intCD
                canBeUsedOnVehicle = currVehIntD not in deny and (len(allow) == 0 or currVehIntD in allow)
                if isHiddenGroup:
                    hasItemsInHangar = CustomizationHelper.areItemsInHangar(CUSTOMIZATION_ITEM_TYPE.EMBLEM, emblemIDs, self._nationID)
                if canBeUsedOnVehicle and (isHasNew or hasItemsInHangar or not isHiddenGroup) and (gui.GUI_SETTINGS.igrEnabled or not gui.GUI_SETTINGS.igrEnabled and igrType == constants.IGR_TYPE.NONE) and (nations is None or g_currentVehicle.item.nationID in nations):
                    result.append({'name': name,
                     'userString': groupUserString,
                     'hasNew': isHasNew,
                     'isIGR': igrType != constants.IGR_TYPE.NONE,
                     'enabled': igrType == constants.IGR_TYPE.NONE or igrType <= igrRoomType,
                     'tooltip': TOOLTIPS.CUSTOMIZATION_EMBLEM_IGR})

        self._list = sorted(result, cmp=self.__comparator)
        return

    def emptyItem(self):
        return {'name': None,
         'userString': '',
         'hasNew': False,
         'isIGR': False,
         'enabled': False}

    def __comparator(self, item, other):
        if item.get('isIGR') == other.get('isIGR'):
            return cmp(item.get('name'), other.get('name'))
        elif item.get('isIGR'):
            return -1
        else:
            return 1


class EmblemsDataProvider(BaseCustomizationDataProvider):

    def __init__(self, nationID, position):
        super(EmblemsDataProvider, self).__init__(nationID)
        self._currentType = CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE
        self.position = position

    @classmethod
    def _makeTextureUrl(cls, width, height, texture, itemSize, coords):
        if texture is None or len(texture) == 0:
            return ''
        else:
            if texture.startswith('gui'):
                texture = texture.replace('gui', '..', 1)
            return texture

    @classmethod
    def _makeSmallTextureUrl(cls, texture, itemSize, coords):
        return EmblemsDataProvider._makeTextureUrl(67, 67, texture, itemSize, coords)

    @classmethod
    def _makeDescription(cls, groupName, userString):
        result = ''
        if len(groupName) > 0 and len(userString) > 0:
            result = makeTooltip(header=groupName, body=userString)
        return result

    def makeItem(self, itemID, isCurrent, lifeCycle, timeLeftString):
        groups, emblems, names = vehicles.g_cache.playerEmblems()
        itemInfo = None
        if emblems is not None:
            itemInfo = self._constructEmblem(itemID, groups, emblems, self.position, isCurrent, CustomizationHelper.isItemInHangar(CUSTOMIZATION_ITEM_TYPE.EMBLEM, itemID, self.nationID, self.position))
        if itemInfo is not None:
            itemInfo['timeLeft'] = timeLeftString
        else:
            itemInfo = {'id': itemID,
             'texturePath': None,
             'description': '',
             'userString': '',
             'igrType': 0,
             'position': self.position,
             'price': {'cost': 0,
                       'isGold': False},
             'action': None,
             'current': isCurrent,
             'isInHangar': False,
             'timeLeft': timeLeftString}
        itemInfo['type'] = CUSTOMIZATION_ITEM_TYPE.EMBLEM
        return itemInfo

    def _constructEmblem(self, itemID, groups, emblems, position, isCurrent = False, isInHangar = False, withoutCheck = True):
        itemInfo = None
        emblem = emblems.get(itemID, None)
        priceFactors = g_itemsCache.items.shop.getEmblemsGroupPriceFactors()
        defPriceFactors = g_itemsCache.items.shop.defaults.getEmblemsGroupPriceFactors()
        hiddens = g_itemsCache.items.shop.getEmblemsGroupHiddens()
        if emblem is not None:
            groupName, igrType, texture, bumpMap, emblemUserString, isMirrored = emblem[0:6]
            emblemIDs, groupUserString, igrType, nations, allow, deny = groups.get(groupName)
            isNewItem = self.isNewID(itemID)
            if withoutCheck or isNewItem or isInHangar or groupName not in hiddens:
                price = self._makeCost(self._cost, self._vehPriceFactor, priceFactors.get(groupName)) if not isInHangar else 0
                defaultPrice = self._makeCost(self._defCost, self._defVehPriceFactor, defPriceFactors.get(groupName, 1)) if not isInHangar else 0
                action = None
                if price != defaultPrice:
                    isPremium = self._isGold == 1
                    newPrice = (0, price) if isPremium else (price, 0)
                    oldPrice = (0, defaultPrice) if isPremium else (defaultPrice, 0)
                    state = (None, ACTION_TOOLTIPS_STATE.DISCOUNT) if isPremium else (ACTION_TOOLTIPS_STATE.DISCOUNT, None)
                    key = 'emblemPacket7Cost'
                    if self._period == 0:
                        key = 'emblemPacketInfCost'
                    elif self._period == 30:
                        key = 'emblemPacket30Cost'
                    action = {'type': ACTION_TOOLTIPS_TYPE.EMBLEMS,
                     'key': cPickle.dumps((groupName, key)),
                     'isBuying': True,
                     'state': state,
                     'newPrice': newPrice,
                     'oldPrice': oldPrice}
                timeLeftStr = ''
                days = 0
                timeLeft = 0 if self._isGold else self._period * 86400
                isPermanent = False
                value = None
                canUse = True
                if isInHangar:
                    item = CustomizationHelper.getItemFromHangar(CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE, itemID, self.nationID, self.position)
                    if item:
                        isPermanent = item.get('isPermanent')
                        value = item.get('quantity')
                        timeLeft = value * 86400 if not item.get('isPermanent') else 0
                        timeLeftStr = CustomizationHelper.getTimeLeftText(timeLeft)
                        if not isPermanent:
                            selectedEmblems, _ = VehicleCustomizationModel.getVehicleModel()
                            for selectedEmblem in selectedEmblems:
                                if selectedEmblems.index(selectedEmblem) != self.position and selectedEmblem[0] == itemID:
                                    canUse = False

                if isCurrent:
                    updatedDescr = CustomizationHelper.getUpdatedDescriptor(g_currentVehicle.item.descriptor)
                    emblem = updatedDescr.playerEmblems[self.position]
                    _, startTime, days = emblem
                    if days:
                        timeLeft = startTime + days * 86400 - time.time()
                    timeLeftStr = CustomizationHelper.getTimeLeftText(timeLeft)
                itemInfo = {'id': itemID,
                 'texturePath': self._makeSmallTextureUrl(texture, None, None),
                 'description': self._makeDescription(groupUserString, emblemUserString),
                 'userString': i18n.makeString(emblemUserString),
                 'igrType': igrType,
                 'position': self.position,
                 'price': {'cost': price,
                           'isGold': days == 0 if isCurrent else self._isGold == 1},
                 'action': action,
                 'current': isCurrent,
                 'isInHangar': isInHangar,
                 'isNew': isNewItem,
                 'timeLeftStr': timeLeftStr,
                 'type': CUSTOMIZATION_ITEM_TYPE.EMBLEM,
                 'isSpecialTooltip': True,
                 'timeLeftValue': timeLeft,
                 'isPermanent': isPermanent,
                 'value': value,
                 'canUse': canUse}
        return itemInfo

    def _getPriceFactor(self, itemID):
        priceFactor = 0
        groups, emblems, names = vehicles.g_cache.playerEmblems()
        emblem = emblems.get(itemID)
        if emblem is not None:
            groupName, igrType, texture, bumpFile, emblemUserString, isMirrored = emblem[0:6]
            if not CustomizationHelper.isItemInHangar(CUSTOMIZATION_ITEM_TYPE.EMBLEM, itemID, self.nationID, self.position):
                priceFactor = g_itemsCache.items.shop.getEmblemsGroupPriceFactors().get(groupName)
        return priceFactor

    def getCostForPackagePrice(self, itemID, packagePrice, isGold):
        return (-1, False)

    def setVehicleTypeParams(self, vehPriceFactor, defaultVehPriceFactor, itemID):
        self._vehPriceFactor = vehPriceFactor
        self._defVehPriceFactor = defaultVehPriceFactor
        self.currentItemID = itemID

    def __comparator(self, item, other):
        if item['current'] ^ other['current']:
            result = -1 if item['current'] else 1
        elif item['isInHangar'] ^ other['isInHangar']:
            result = -1 if item['isInHangar'] else 1
        else:
            result = cmp(item['userString'], other['userString'])
        return result

    def _populate(self):
        super(EmblemsDataProvider, self)._populate()
        LOG_DEBUG('EmblemsDataProvider _populate')

    def _dispose(self):
        LOG_DEBUG('EmblemsDataProvider _dispose')
        super(EmblemsDataProvider, self)._dispose()

    def onRequestList(self, groupName):
        groups, emblems, names = vehicles.g_cache.playerEmblems()
        group = groups.get(groupName)
        result = []
        hiddenItems = g_itemsCache.items.shop.getEmblemsGroupHiddens()
        if group is not None:
            emblemIDs, groupUserString, igrType, nations, allow, deny = group
            self._isIGR = igrType != constants.IGR_TYPE.NONE
            isHasNew = self._hasNewItems(CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE, emblemIDs)
            isHiddenGroup = groupName in hiddenItems
            hasItemsInHangar = False
            if isHiddenGroup:
                hasItemsInHangar = CustomizationHelper.areItemsInHangar(CUSTOMIZATION_ITEM_TYPE.EMBLEM, emblemIDs, self.nationID)
            if isHasNew or hasItemsInHangar or not isHiddenGroup:
                for id in emblemIDs:
                    itemInfo = self._constructEmblem(id, groups, emblems, self.position, self.currentItemID == id, False if self.isIGRItem(id) else CustomizationHelper.isItemInHangar(CUSTOMIZATION_ITEM_TYPE.EMBLEM, id, self.nationID, self.position), False)
                    if itemInfo is not None:
                        if not self._isIGR or self._isIGR and itemInfo.get('igrType') != constants.IGR_TYPE.NONE:
                            result.append(itemInfo)

        return sorted(result, cmp=self.__comparator)

    def isIGRItem(self, itemID):
        groups, emblems, names = vehicles.g_cache.playerEmblems()
        if itemID is not None:
            for groupName, group in groups.iteritems():
                emblemIDs, groupUserString, igrType, nations, allow, deny = group
                if itemID in emblemIDs:
                    return igrType != constants.IGR_TYPE.NONE

        return False


class InscriptionDataProvider(EmblemsDataProvider):

    def __init__(self, nationID, position):
        super(InscriptionDataProvider, self).__init__(nationID, position)
        self._currentType = CUSTOMIZATION_ITEM_TYPE.INSCRIPTION_TYPE

    @classmethod
    def _makeSmallTextureUrl(cls, texture, itemSize, coords):
        return EmblemsDataProvider._makeTextureUrl(150, 76, texture, itemSize, coords)

    def makeItem(self, itemID, isCurrent, lifeCycle, timeLeftString):
        customization = vehicles.g_cache.customization(self.nationID)
        itemInfo = None
        if customization is not None:
            groups = customization.get('inscriptionGroups', {})
            inscriptions = customization.get('inscriptions', {})
            if inscriptions is not None:
                itemInfo = self._constructInscription(itemID, groups, inscriptions, isCurrent, CustomizationHelper.isItemInHangar(CUSTOMIZATION_ITEM_TYPE.INSCRIPTION, itemID, self.nationID, self.position))
            if itemInfo is not None:
                itemInfo['timeLeft'] = timeLeftString
            else:
                itemInfo = {'timeLeft': timeLeftString,
                 'id': itemID,
                 'texturePath': None,
                 'description': '',
                 'price': {'cost': 0,
                           'isGold': False},
                 'action': None,
                 'current': isCurrent,
                 'position': self.position}
        itemInfo['type'] = CUSTOMIZATION_ITEM_TYPE.INSCRIPTION
        return itemInfo

    def _constructInscription(self, itemID, groups, inscriptions, isCurrent = False, isInHangar = False, withoutCheck = True):
        itemInfo = None
        inscription = inscriptions.get(itemID, None)
        priceFactors = g_itemsCache.items.shop.getInscriptionsGroupPriceFactors(self.nationID)
        defPriceFactors = g_itemsCache.items.shop.defaults.getInscriptionsGroupPriceFactors(self.nationID)
        hiddens = g_itemsCache.items.shop.getInscriptionsGroupHiddens(self.nationID)
        if inscription is not None:
            groupName, igrType, texture, bumpMap, inscriptionUserString, isFeatured = inscription[0:6]
            inscriptionIDs, groupUserString, igrType, allow, deny = groups.get(groupName)
            isNewItem = self.isNewID(itemID)
            if withoutCheck or isNewItem or isInHangar or groupName not in hiddens:
                price = self._makeCost(self._cost, self._vehPriceFactor, priceFactors.get(groupName)) if not isInHangar else 0
                defaultPrice = self._makeCost(self._defCost, self._defVehPriceFactor, defPriceFactors.get(groupName, 1)) if not isInHangar else 0
                action = None
                if price != defaultPrice:
                    isPremium = self._isGold == 1
                    newPrice = (0, price) if isPremium else (price, 0)
                    oldPrice = (0, defaultPrice) if isPremium else (defaultPrice, 0)
                    state = (None, ACTION_TOOLTIPS_STATE.DISCOUNT) if isPremium else (ACTION_TOOLTIPS_STATE.DISCOUNT, None)
                    key = 'inscriptionPacket7Cost'
                    if self._period == 0:
                        key = 'inscriptionPacketInfCost'
                    elif self._period == 30:
                        key = 'inscriptionPacket30Cost'
                    action = {'type': ACTION_TOOLTIPS_TYPE.ECONOMICS,
                     'key': key,
                     'isBuying': True,
                     'state': state,
                     'newPrice': newPrice,
                     'oldPrice': oldPrice}
                timeLeftStr = ''
                days = 0
                isPermanent = False
                value = 0
                timeLeft = 0 if self._isGold else self._period * 86400
                canUse = True
                if isInHangar:
                    item = CustomizationHelper.getItemFromHangar(CUSTOMIZATION_ITEM_TYPE.INSCRIPTION_TYPE, itemID, self.nationID, self.position)
                    if item:
                        isPermanent = item.get('isPermanent')
                        value = item.get('quantity')
                        timeLeft = value * 86400 if not item.get('isPermanent') else 0
                        timeLeftStr = CustomizationHelper.getTimeLeftText(timeLeft)
                        if not isPermanent:
                            _, selectedInscriptions = VehicleCustomizationModel.getVehicleModel()
                            for selectedInscription in selectedInscriptions:
                                if selectedInscriptions.index(selectedInscription) != self.position and selectedInscription[0] == itemID:
                                    canUse = False

                if isCurrent:
                    updatedDescr = CustomizationHelper.getUpdatedDescriptor(g_currentVehicle.item.descriptor)
                    item = updatedDescr.playerInscriptions[self.position]
                    _, startTime, days, _ = item
                    if days:
                        timeLeft = startTime + days * 86400 - time.time()
                    timeLeftStr = CustomizationHelper.getTimeLeftText(timeLeft)
                itemInfo = {'id': itemID,
                 'texturePath': self._makeSmallTextureUrl(texture, None, None),
                 'description': self._makeDescription(groupUserString, inscriptionUserString),
                 'igrType': igrType,
                 'price': {'cost': price,
                           'isGold': days == 0 if isCurrent else self._isGold == 1},
                 'action': action,
                 'current': isCurrent,
                 'position': self.position,
                 'isInHangar': isInHangar,
                 'isFeatured': isFeatured,
                 'isNew': isNewItem,
                 'timeLeftStr': timeLeftStr,
                 'type': CUSTOMIZATION_ITEM_TYPE.INSCRIPTION,
                 'nationId': self.nationID,
                 'isSpecialTooltip': True,
                 'timeLeftValue': timeLeft,
                 'isPermanent': isPermanent,
                 'value': value,
                 'canUse': canUse}
        return itemInfo

    def _getPriceFactor(self, itemID):
        priceFactor = 0
        customization = vehicles.g_cache.customization(self.nationID)
        if customization is not None:
            inscriptions = customization.get('inscriptions', {})
            inscription = inscriptions.get(itemID)
            if inscription is not None:
                groupName, igrType, texture, bumpMap, inscriptionUserString, isFeatured = inscription[0:6]
                if not CustomizationHelper.isItemInHangar(CUSTOMIZATION_ITEM_TYPE.INSCRIPTION, itemID, self.nationID, self.position):
                    priceFactor = g_itemsCache.items.shop.getInscriptionsGroupPriceFactors(self.nationID).get(groupName)
        return priceFactor

    def getCostForPackagePrice(self, itemID, packagePrice, isGold):
        return (-1, False)

    def onRequestList(self, groupName):
        if not groupName:
            return
        else:
            customization = vehicles.g_cache.customization(self.nationID)
            result = []
            hiddenItems = g_itemsCache.items.shop.getInscriptionsGroupHiddens(self.nationID)
            if customization is not None:
                groups = customization.get('inscriptionGroups', {})
                group = groups.get(groupName, {})
                inscriptions = customization.get('inscriptions', {})
                if group is not None:
                    inscriptionIDs, groupUserString, igrType, allow, deny = group
                    isHasNew = self._hasNewItems(CUSTOMIZATION_ITEM_TYPE.INSCRIPTION_TYPE, inscriptionIDs)
                    isHiddenGroup = groupName in hiddenItems
                    hasItemsInHangar = False
                    if isHiddenGroup:
                        hasItemsInHangar = CustomizationHelper.areItemsInHangar(CUSTOMIZATION_ITEM_TYPE.INSCRIPTION, inscriptionIDs, self.nationID)
                    self._isIGR = igrType != constants.IGR_TYPE.NONE
                    if isHasNew or hasItemsInHangar or not isHiddenGroup:
                        for id in inscriptionIDs:
                            itemInfo = self._constructInscription(id, groups, inscriptions, self.currentItemID == id, False if self.isIGRItem(id) else CustomizationHelper.isItemInHangar(CUSTOMIZATION_ITEM_TYPE.INSCRIPTION, id, self.nationID, self.position), False)
                            if itemInfo is not None:
                                if not self._isIGR or self._isIGR and itemInfo.get('igrType') != constants.IGR_TYPE.NONE:
                                    result.append(itemInfo)

            return sorted(result, cmp=self.__comparator)

    def isIGRItem(self, itemID):
        customization = vehicles.g_cache.customization(self.nationID)
        groups = customization.get('inscriptionGroups', {})
        if itemID is not None:
            for groupName, group in groups.iteritems():
                emblemIDs, groupUserString, igrType, allow, deny = group
                if itemID in emblemIDs:
                    return igrType != constants.IGR_TYPE.NONE

        return False

    def __comparator(self, item, other):
        if item['current'] ^ other['current']:
            result = -1 if item['current'] else 1
        elif item['isInHangar'] ^ other['isInHangar']:
            result = -1 if item['isInHangar'] else 1
        elif item['isFeatured'] ^ other['isFeatured']:
            result = -1 if item['isFeatured'] else 1
        else:
            result = cmp(item['id'], other['id'])
        return result


class CamouflagesDataProvider(BaseCustomizationDataProvider):

    def __init__(self, nationID):
        super(CamouflagesDataProvider, self).__init__(nationID)
        self._currentType = CUSTOMIZATION_ITEM_TYPE.CAMOUFLAGE_TYPE
        self.currentGroup = None
        return

    @classmethod
    def _makeTextureUrl(cls, width, height, texture, colors, armorColor, lifeCycle = None):
        if texture is None or len(texture) == 0:
            return ''
        else:
            weights = Math.Vector4((colors[0] >> 24) / 255.0, (colors[1] >> 24) / 255.0, (colors[2] >> 24) / 255.0, (colors[3] >> 24) / 255.0)
            if lifeCycle is not None:
                startTime, days = lifeCycle
                if days > 0:
                    timeAmount = float((time.time() - startTime) / (days * 86400))
                    if timeAmount > 1.0:
                        weights *= _CAMOUFLAGE_MIN_INTENSITY
                    elif timeAmount > 0:
                        weights *= (1.0 - timeAmount) * (1.0 - _CAMOUFLAGE_MIN_INTENSITY) + _CAMOUFLAGE_MIN_INTENSITY
            return 'img://camouflage,{0:d},{1:d},"{2:>s}",{3[0]:d},{3[1]:d},{3[2]:d},{3[3]:d},{4[0]:n},{4[1]:n},{4[2]:n},{4[3]:n},{5:d}'.format(width, height, texture, colors, weights, armorColor)

    @classmethod
    def _makeSmallTextureUrl(cls, texture, colors, armorColor, lifeCycle = None):
        return CamouflagesDataProvider._makeTextureUrl(67, 67, texture, colors, armorColor, lifeCycle=lifeCycle)

    @classmethod
    def _makeDescription(cls, groups, groupName, description):
        if not (description and groupName):
            return ''
        name = groups.get(groupName, {}).get('userString')
        return makeTooltip(header=name, body=description)

    def getCamouflageDescr(self, camouflageID):
        camouflage = None
        customization = vehicles.g_cache.customization(self.nationID)
        if customization is not None:
            camouflages = customization.get('camouflages', {})
            camouflage = camouflages.get(camouflageID, None)
        return camouflage

    def makeItem(self, camouflageID, isCurrent, lifeCycle, timeLeftString, kind):
        customization = vehicles.g_cache.customization(self.nationID)
        camouflageInfo = None
        if customization is not None:
            groups = customization.get('camouflageGroups', {})
            armorColor = customization.get('armorColor', 0)
            camouflageInfo = self._constructCamouflage(camouflageID, groups, customization.get('camouflages', {}), armorColor, lifeCycle, isCurrent, CustomizationHelper.isItemInHangar(CUSTOMIZATION_ITEM_TYPE.CAMOUFLAGE, camouflageID, self.nationID))
        if camouflageInfo is not None:
            camouflageInfo['timeLeft'] = timeLeftString
        else:
            camouflageInfo = {'timeLeft': timeLeftString,
             'id': camouflageID,
             'texturePath': None,
             'description': self.getDefaultDescription(kind),
             'price': {'cost': 0,
                       'isGold': False},
             'action': None,
             'isNew': False,
             'invisibilityLbl': '',
             'current': False}
        return camouflageInfo

    def _constructCamouflage(self, cID, groups, camouflages, armorColor, lifeCycle = None, isCurrent = False, isInHangar = False, withoutCheck = True, currVehIntD = None):
        camouflageInfo = None
        camouflage = camouflages.get(cID, None)
        hiddenCamos = g_itemsCache.items.shop.getCamouflagesHiddens(self.nationID)
        if camouflage is not None and (withoutCheck or cID not in hiddenCamos or isInHangar or camouflage.get('igrType', 0) != constants.IGR_TYPE.NONE and cID not in hiddenCamos):
            denyCD = camouflage.get('deny')
            allowCD = camouflage.get('allow')
            if currVehIntD not in denyCD and (len(allowCD) == 0 or currVehIntD in allowCD) or currVehIntD is None:
                invisibilityFactor = camouflage.get('invisibilityFactor', 1)
                invisibilityPercent = int(round((invisibilityFactor - 1) * 100))
                invisibilityLbl = gui.makeHtmlString('html_templates:lobby/customization', 'camouflage-hint', {'percents': invisibilityPercent}, sourceKey=self.__getKindById(camouflage.get('kind', 0)))
                price = self._makeCost(self._cost, self._vehPriceFactor, self._getPriceFactor(cID)) if not isInHangar else 0
                defaultPrice = self._makeCost(self._defCost, self._defVehPriceFactor, self._getDefaultCamoPriceFactor(cID)) if not isInHangar else 0
                action = None
                if price != defaultPrice:
                    isPremium = self._isGold == 1
                    newPrice = (0, price) if isPremium else (price, 0)
                    oldPrice = (0, defaultPrice) if isPremium else (defaultPrice, 0)
                    state = (None, ACTION_TOOLTIPS_STATE.DISCOUNT) if isPremium else (ACTION_TOOLTIPS_STATE.DISCOUNT, None)
                    key = 'camouflagePacket7Cost'
                    if self._period == 0:
                        key = 'camouflagePacketInfCost'
                    elif self._period == 30:
                        key = 'camouflagePacket30Cost'
                    action = {'type': ACTION_TOOLTIPS_TYPE.CAMOUFLAGE,
                     'key': cPickle.dumps((currVehIntD, key)),
                     'isBuying': True,
                     'state': state,
                     'newPrice': newPrice,
                     'oldPrice': oldPrice}
                timeLeftStr = ''
                days = 0
                isPermanent = False
                value = 0
                timeLeft = 0 if self._isGold else self._period * 86400
                if isInHangar:
                    item = CustomizationHelper.getItemFromHangar(CUSTOMIZATION_ITEM_TYPE.CAMOUFLAGE_TYPE, cID, self.nationID)
                    if item:
                        isPermanent = item.get('isPermanent')
                        value = item.get('quantity')
                        timeLeft = value * 86400 if not item.get('isPermanent') else 0
                        timeLeftStr = CustomizationHelper.getTimeLeftText(timeLeft)
                if isCurrent:
                    updatedDescr = CustomizationHelper.getUpdatedDescriptor(g_currentVehicle.item.descriptor)
                    item = updatedDescr.camouflages[camouflage.get('kind', 0)]
                    _, startTime, days = item
                    if days:
                        timeLeft = startTime + days * 86400 - time.time()
                    timeLeftStr = CustomizationHelper.getTimeLeftText(timeLeft)
                camouflageInfo = {'id': cID,
                 'texturePath': self._makeSmallTextureUrl(camouflage.get('texture'), camouflage.get('colors', (0, 0, 0, 0)), armorColor, lifeCycle),
                 'description': self._makeDescription(groups, camouflage.get('groupName', ''), camouflage.get('description', '')),
                 'price': {'cost': price,
                           'isGold': self._isGold == 1},
                 'action': action,
                 'isNew': self.isNewID(cID),
                 'invisibilityLbl': invisibilityLbl,
                 'igrType': camouflage.get('igrType', 0),
                 'current': isCurrent,
                 'isInHangar': isInHangar,
                 'timeLeftStr': timeLeftStr,
                 'type': CUSTOMIZATION_ITEM_TYPE.CAMOUFLAGE,
                 'nationId': self.nationID,
                 'isSpecialTooltip': True,
                 'timeLeftValue': timeLeft,
                 'isPermanent': isPermanent,
                 'value': value}
        return camouflageInfo

    def getCostForPackagePrice(self, camouflageID, packagePrice, isGold):
        if CustomizationHelper.isItemInHangar(CUSTOMIZATION_ITEM_TYPE.CAMOUFLAGE, camouflageID, self.nationID):
            priceFactor = 0
        else:
            priceFactor = g_itemsCache.items.shop.getCamouflagesPriceFactors(self.nationID).get(camouflageID)
        return (self._makeCost(packagePrice, self._vehPriceFactor, priceFactor), isGold)

    def setVehicleTypeParams(self, vehPriceFactor, defaultVehPriceFactor, camouflageID):
        self._vehPriceFactor = vehPriceFactor
        self._defVehPriceFactor = defaultVehPriceFactor
        self.currentItemID = camouflageID

    def __comparator(self, item, other):
        if item['current'] ^ other['current']:
            result = -1 if item['current'] else 1
        elif item['isInHangar'] ^ other['isInHangar']:
            result = -1 if item['isInHangar'] else 1
        elif item['isNew'] ^ other['isNew']:
            result = -1 if item['isNew'] else 1
        else:
            result = cmp(item['id'], other['id'])
        return result

    def __getKindById(self, kindId):
        kind = 'winter'
        for k, v in CAMOUFLAGE_KINDS.iteritems():
            if v == kindId:
                kind = k

        return kind

    def _populate(self):
        super(CamouflagesDataProvider, self)._populate()
        LOG_DEBUG('CamouflagesDataProvider _populate')

    def _dispose(self):
        LOG_DEBUG('CamouflagesDataProvider _dispose')
        super(CamouflagesDataProvider, self)._dispose()

    def getDefaultHintText(self, _):
        return gui.makeHtmlString('html_templates:lobby/customization', 'camouflage-hint', sourceKey='default')

    def getDefaultDescription(self, kindID):
        kindKey = '#tooltips:customization/camouflage/{0:>s}'.format(self.__getKindById(kindID))
        bodyKey = TOOLTIPS.CUSTOMIZATION_CAMOUFLAGE_EMPTY
        return makeTooltip(body=i18n.makeString(bodyKey, kind=i18n.makeString(kindKey)))

    def setGroupCurrentItemId(self, itemId):
        self.currentItemID = int(itemId) if itemId is not None else None
        return

    def onRequestList(self, groupName):
        self.currentGroup = groupName
        customization = vehicles.g_cache.customization(self.nationID)
        result = []
        if customization is not None:
            groups = customization.get('camouflageGroups', {})
            group = groups.get(groupName, {})
            camouflages = customization.get('camouflages', {})
            armorColor = customization.get('armorColor', 0)
            ids = group.get('ids', [])
            currIntDescr = g_currentVehicle.item.intCD
            for id in ids:
                camouflageInfo = self._constructCamouflage(id, groups, camouflages, armorColor, isCurrent=self.currentItemID == id, isInHangar=CustomizationHelper.isItemInHangar(CUSTOMIZATION_ITEM_TYPE.CAMOUFLAGE, id, self.nationID), withoutCheck=False, currVehIntD=currIntDescr)
                if camouflageInfo is not None:
                    if not self._isIGR and camouflageInfo.get('igrType') == constants.IGR_TYPE.NONE or self._isIGR and camouflageInfo.get('igrType') == constants.IGR_TYPE.PREMIUM:
                        result.append(camouflageInfo)

            if gui.GUI_SETTINGS.igrEnabled:
                for name, group in groups.iteritems():
                    if name not in CAMOUFLAGE_KINDS:
                        ids = group.get('ids', [])
                        for cID in ids:
                            camouflage = camouflages.get(cID, None)
                            if camouflage.get('kind', 0) == CAMOUFLAGE_KINDS.get(groupName, 0):
                                camouflageInfo = self._constructCamouflage(cID, groups, camouflages, armorColor, isCurrent=self.currentItemID == cID, isInHangar=CustomizationHelper.isItemInHangar(CUSTOMIZATION_ITEM_TYPE.CAMOUFLAGE, cID, self.nationID), withoutCheck=False, currVehIntD=currIntDescr)
                                if camouflageInfo is not None and camouflageInfo:
                                    if not self._isIGR and camouflageInfo.get('igrType') == constants.IGR_TYPE.NONE or self._isIGR and camouflageInfo.get('igrType') == constants.IGR_TYPE.PREMIUM:
                                        result.append(camouflageInfo)

        return sorted(result, cmp=self.__comparator)

    def isIGRItem(self, itemID):
        customization = vehicles.g_cache.customization(self.nationID)
        groups = customization.get('camouflageGroups', {})
        if itemID is not None:
            for groupName, group in groups.iteritems():
                ids = group.get('ids', [])
                if itemID in ids:
                    return group.get('igrType', 0) != constants.IGR_TYPE.NONE

        return False

    def _getPriceFactor(self, camoID):
        return g_itemsCache.items.shop.getCamouflagesPriceFactors(self.nationID).get(camoID)

    def _getDefaultCamoPriceFactor(self, camoID):
        return g_itemsCache.items.shop.defaults.getCamouflagesPriceFactors(self.nationID).get(camoID)


class ITEM_REMOVE_TYPE():
    NONE = 0
    DESTROY = 1
    STORED = 2
