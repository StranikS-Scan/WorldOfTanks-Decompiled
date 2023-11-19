# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/awards/items_collection_provider.py
import logging
from copy import deepcopy
import typing
from adisp import adisp_async, adisp_process
from gui.battle_pass.battle_pass_award import awardsFactory
from gui.impl.lobby.awards.packers import getMultipleAwardsBonusPacker
from gui.impl.lobby.awards.prefetch import PREFETCHERS
from gui.server_events.bonuses import mergeBonuses
from helpers import dependency
from items.components.component_constants import EMPTY_TUPLE
from skeletons.gui.platform.catalog_service_controller import IPurchaseCache
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
    from gui.impl.backport import TooltipData
    from gui.platform.catalog_service.controller import _PurchaseDescriptor
    from gui.platform.catalog_service.controller import _ProductExtraData
_logger = logging.getLogger(__name__)

def _addCompensation(compensation, toUpdate):
    for ckey, cValue in compensation.iteritems():
        if ckey not in toUpdate:
            toUpdate[ckey] = cValue
        toUpdDataStruct = toUpdate[ckey]
        if isinstance(cValue, dict):
            if isinstance(toUpdDataStruct, dict):
                toUpdDataStruct.update(cValue)
            elif isinstance(toUpdDataStruct, list):
                for kCV, vCV in cValue.iteritems():
                    toUpdDataStruct.append({kCV: vCV})

        if isinstance(cValue, list):
            if isinstance(toUpdDataStruct, list):
                toUpdDataStruct.extend(cValue)
            else:
                _logger.warning('The type of compensation and updatable must be list! Updatable is %s, item=%s', type(toUpdDataStruct).__name__, toUpdDataStruct)
        _logger.warning('Unsupported data type for compensation applying: %')


class _OrderHelper(object):

    @classmethod
    def buildSortedBonusList(cls, validData, order, entitlements):
        codeOrder = {entitlement.get('code'):entitlement.get('order', 0) for entitlement in entitlements}
        order.sort(key=lambda x: codeOrder.get(x[1], 0))
        order = [ item[0] for item in order ]
        sortedList = []
        for oItem in order:
            for orderK, orderV in oItem.iteritems():
                if orderK in validData:
                    validSection = validData[orderK]
                    if isinstance(orderV, dict):
                        for orderKV in orderV.iterkeys():
                            validItem = cls._getItemByDictKey(orderKV, validSection)
                            if validItem is not None:
                                sortedList.append({orderK: {orderKV: validItem}})
                                if not validSection:
                                    del validData[orderK]

                    elif isinstance(orderV, (list, tuple)):
                        if orderV:
                            firstListItem = orderV[0]
                            if isinstance(firstListItem, dict):
                                if 'id' in firstListItem:
                                    for oVItem in orderV:
                                        validItem = cls._getItemByID(oVItem['id'], validSection)
                                        if validItem is not None:
                                            sortedList.append({orderK: [validItem]})
                                            if not validSection:
                                                del validData[orderK]

                                else:
                                    sortedList.append({orderK: validSection})
                                    del validData[orderK]
                            else:
                                _logger.warning('Unsupported list item data type: %s, item=%s', type(firstListItem).__name__, firstListItem)
                    else:
                        sortedList.append({orderK: validSection})
                        del validData[orderK]

        if validData:
            sortedList.append(validData)
        return sortedList

    @classmethod
    def _getItemByDictKey(cls, key, validSection):
        if isinstance(validSection, dict):
            if key in validSection:
                obj = validSection[key]
                del validSection[key]
                return obj
        elif isinstance(validSection, (tuple, list)):
            itemVal = None
            for i, vItem in enumerate(validSection):
                if isinstance(vItem, dict):
                    if key in vItem:
                        itemVal = vItem[key]
                        validSection.pop(i)
                        break
            else:
                _logger.debug("Couldn't find any item with intCD=%s in %s", key, validSection)

            return itemVal
        _logger.warning('Unsupported data format! Expected list or dict but %s received! Data: %s', type(validSection).__name__, validSection)
        return

    @classmethod
    def _getItemByID(cls, itemID, validSection):
        for i, vItem in enumerate(validSection):
            if isinstance(vItem, dict) and 'id' in vItem:
                if itemID == vItem['id']:
                    validSection.pop(i)
                    return vItem
            _logger.warning('"id" key has not been found in data item: %s in %s', vItem, validSection)

        return None


@adisp_async
@adisp_process
def packBonusModelAndTooltipData(bonuses, productCode, callback=None):
    bonusIndexTotal = 0
    tooltipData = {}
    bonusModelsList = []
    yield lambda callback: callback(True)
    packer = getMultipleAwardsBonusPacker(productCode)
    for bonus in bonuses:
        if bonus.isShowInGUI():
            bonusList = yield packer.requestData(bonus)
            bonusTooltipList = []
            bonusContentIdList = []
            if bonusList and tooltipData is not None:
                bonusTooltipList = yield packer.requestToolTip(bonus)
                bonusContentIdList = packer.getContentId(bonus)
            for bonusIndex, item in enumerate(bonusList):
                item.setIndex(bonusIndex)
                bonusModelsList.append(item)
                if tooltipData is not None:
                    tooltipIdx = str(bonusIndexTotal)
                    item.setTooltipId(tooltipIdx)
                    if bonusTooltipList:
                        tooltipData[tooltipIdx] = bonusTooltipList[bonusIndex]
                    if bonusContentIdList:
                        item.setTooltipContentId(str(bonusContentIdList[bonusIndex]))
                    bonusIndexTotal += 1
                if len(bonusModelsList) >= 10:
                    callback((bonusModelsList, tooltipData))
                    return

    callback((bonusModelsList, tooltipData))
    return


class MultipleAwardRewardsMainPacker(object):
    __purchaseCache = dependency.descriptor(IPurchaseCache)

    @adisp_async
    @adisp_process
    def getWholeBonusesData(self, invoiceData, productCode, callback=None):
        yield lambda callback: callback(True)
        metaData = invoiceData.get('meta', {})
        if productCode:
            purchasePackage = yield self.__purchaseCache.requestPurchaseByID(productCode)
            bonusData = deepcopy(invoiceData['data'])
            compensation = deepcopy(invoiceData.get('compensation', {}))
            vehCompensation = compensation.get('vehicles', {})
            for k in vehCompensation:
                if not vehCompensation[k]:
                    vehCompensation[k] = {'rent': {'battles': 1}}

            _addCompensation(compensation, bonusData)
            sortedBList = _OrderHelper.buildSortedBonusList(bonusData, metaData.get('order', EMPTY_TUPLE), purchasePackage.getEntitlements())
            self.__extendSortedBonusList(sortedBList, purchasePackage.getExtraData())
            bonuses = []
            for bData in sortedBList:
                bonuses.extend(awardsFactory(bData))

            bonuses = mergeBonuses(bonuses)
            if self.__prefetchEssentialData(bonuses, productCode):
                viewRewards, tooltipItems = yield packBonusModelAndTooltipData(bonuses, productCode)
                if viewRewards:
                    callback((viewRewards, tooltipItems))
                    return
        callback((EMPTY_TUPLE, EMPTY_TUPLE))

    def __extendSortedBonusList(self, sortedBList, extraData):
        for order, extItem in extraData.iterItems():
            sortedBList.insert(order, extItem)

    def __prefetchEssentialData(self, bonuses, productCode):
        for bonus in bonuses:
            prefetcherCls = PREFETCHERS.get(bonus.getName())
            if prefetcherCls:
                if not prefetcherCls(productCode).prefetch(bonus):
                    return False

        return True
