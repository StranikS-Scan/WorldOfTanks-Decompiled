# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_processor.py
import logging
import typing
import AccountCommands
from constants import MAX_VEHICLE_LEVEL
from festivity.base import BaseFestivityProcessor
from frameworks.wulf import WindowLayer
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.gf_builders import ConfirmCancelDialogBuilder
from gui.impl.lobby.new_year.dialogs.dialogs import showBuyDialog, showFullscreenConfirmDialog, showResourcesConvertDialog, showSetAutoCollectingDialog, showCustomizationBuyDialog
from gui.impl.lobby.new_year.marketplace import bonusChecker
from gui.impl.gen import R
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.gui_items.processors.plugins import SyncValidator
from gui.shared.money import Currency
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.requesters import REQ_CRITERIA
from items import new_year
from helpers import dependency
from gui.shared.gui_items.processors import Processor, makeI18nError, plugins, makeSuccess, makeError
from items.components.ny_constants import CELEBRITY_LOCK_ARENA_BONUS_TYPES, NY_CURRENCY_NAME_TO_IDX, CELEBRITY_LOCK_VEHICLE_MIN_LEVEL, NyCurrency, CelebrityQuestTokenParts, NY_CURRENCY_IDX_TO_NAME
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from items.new_year import getCollectionByIntID
from new_year import makeHangarNameMask
from new_year.gift_machine_helper import getCoinPrice
from new_year.ny_buy_toy_helper import getToyPrice
from new_year.ny_constants import GuestsQuestsTokens
from new_year.ny_marketplace_helper import isCollectionItemReceived
from new_year.ny_resource_collecting_helper import getNextCollectingDescr, getCollectingCooldownTime
from new_year.ny_toy_info import NewYearCurrentToyInfo
from shared_utils import first
from skeletons.festivity_factory import IFestivityFactory
from skeletons.gui.system_messages import ISystemMessages
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
_logger = logging.getLogger()
if typing.TYPE_CHECKING:
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper, FullScreenDialogBaseView
    from ny_common.MarketplaceConfig import CategoryItem
    from frameworks import wulf

class NewYearCommandsProcessor(BaseFestivityProcessor):

    def hangToy(self, toyID, slotID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_SLOT_FILL, (slotID, toyID), callback)

    def applyVariadicDiscount(self, goodiesID, discountID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_SELECT_DISCOUNT, (goodiesID, discountID), callback)

    def sendSeen(self, slotID):
        self._perform(AccountCommands.CMD_NEW_YEAR_SEE_INVENTORY_TOYS, (slotID,))

    def chooseXPBonus(self, choiceID):
        self._perform(AccountCommands.CMD_NEW_YEAR_CHOOSE_XP_BONUS, (choiceID,))

    def convertResources(self, initialResourceID, receivedResourceID, initialValue, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_CONVERT_RESOURCES, (initialResourceID, receivedResourceID, initialValue), callback)

    def seenInCollection(self, seenToys):
        self._perform(AccountCommands.CMD_NEW_YEAR_SEE_COLLECTION_TOYS, (seenToys,))

    def buyMarketplaceItem(self, categoryID, itemID, resourceID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_BUY_MARKETPLACE_ITEM, (categoryID, itemID, resourceID), callback)

    def rerollCelebrityQuest(self, questID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_REROLL_CELEBRITY_QUEST, (questID,), callback)

    def resetLootboxStatistics(self, boxID, callback=None):
        self._perform(AccountCommands.CMD_LOOTBOX_RESET_STATS, (boxID,), callback)

    def buyCelebrityQuest(self, guestName, questIndex, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_COMPLETE_GUEST_QUEST, (questIndex, guestName), callback)

    def buyObjectLevel(self, objectName, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_UPGRADE_OBJECT_LEVEL, (objectName,), callback)

    def buyNyCoins(self, resourceID, amount, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_BUY_GIFT_MACHINE_COINS, (resourceID, amount), callback)

    def setHangarName(self, titleIndex, descriptionIndex, callback=None):
        mask = makeHangarNameMask(titleIndex, descriptionIndex)
        self._perform(AccountCommands.CMD_NEW_YEAR_SET_HANGAR_NAME_MASK, (mask,), callback)

    def setAutoCollectingResources(self, state, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_SET_AUTO_RESOURCE_COLLECTING_STATE, (state,), callback)

    def manualCollectResources(self, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_MANUAL_RESOURCE_COLLECTING, (1,), callback)

    def buyToy(self, toyID, slotID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_BUY_TOY, (toyID, slotID), callback)

    def addToys(self, toysDict=None):
        toysToAdd = []
        if toysDict:
            for slotID, data in toysDict.iteritems():
                for toyID, count in data.iteritems():
                    toysToAdd.extend([slotID, toyID, count])

        else:
            for slot in new_year.g_cache.slots:
                toys = [ toy for toy in new_year.g_cache.toys.itervalues() if toy.type == slot.type ]
                for toy in toys:
                    toysToAdd.extend([slot.id, toy.id, 1])

        self._perform(AccountCommands.CMD_NEW_YEAR_ADD_TOYS_DEV, (toysToAdd,))

    def addResource(self, count, type):
        self._perform(AccountCommands.CMD_NEW_YEAR_ADD_RESOURCES_DEV, (count, type))

    def strokeDog(self, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_STROKE_DOG, (1,), callback)

    def getNYPiggyBankRewards(self, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_GET_NY_PIGGY_BANK_REWARDS, (1,), callback)


class CraftProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, toyTypeID, settingID, rank, filler):
        super(CraftProcessor, self).__init__()
        self.__toyTypeID = toyTypeID
        self.__settingID = settingID
        self.__rankID = rank
        self.__filler = filler

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/craftToy/server_error')

    def _successHandler(self, code, ctx=None):
        msg = ''
        return makeSuccess(userMsg=msg, auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to craft toyTypeID: %s, settingID: %s, rank: %s', self.__toyTypeID, self.__settingID, self.__rankID)
        self._festivityFactory.getProcessor().craftToy(self.__toyTypeID, self.__settingID, self.__rankID, self.__filler, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class ApplyVehicleDiscountProcessor(Processor):
    _CUSTOM_ERRORS_MAP = {'wrong variadicDiscountID': 'noDiscounts',
     'missing variadic discount': 'noDiscounts',
     'discount already exists': 'alreadyActive',
     'vehicle already in inventory': 'alreadyBought',
     'goodieID': 'noDiscountForVehicle',
     'Goodie with id': 'noDiscountForVehicle'}
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, goodiesID, discountID, **kwargs):
        super(ApplyVehicleDiscountProcessor, self).__init__()
        self.__goodiesID = goodiesID
        self.__discountID = discountID

    def _errorHandler(self, code, errStr='', ctx=None):
        clientErrKey = ''
        for errorMarker, errKey in self._CUSTOM_ERRORS_MAP.iteritems():
            if errStr.startswith(errorMarker):
                clientErrKey = errKey
                break

        if clientErrKey:
            errorStr = backport.text(R.strings.system_messages.newYear.applyVehicleDiscount.server_error.dyn(clientErrKey)())
        else:
            errorStr = backport.text(R.strings.system_messages.newYear.applyVehicleDiscount.server_error())
        return makeError(errorStr, auxData={'clientErrKey': clientErrKey})

    def _request(self, callback):
        _logger.debug('Make server request to apply vehcile discount goodiesID: %s, discountID: %s', self.__goodiesID, self.__discountID)
        self._festivityFactory.getProcessor().applyVariadicDiscount(self.__goodiesID, self.__discountID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class HangToyProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, toyID, slotID):
        super(HangToyProcessor, self).__init__()
        self.__toyID = toyID
        self.__slotID = slotID

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/hangToy/server_error')

    def _request(self, callback):
        self._festivityFactory.getProcessor().hangToy(self.__toyID, self.__slotID, lambda resultID, errorStr, ext: self._response(resultID, callback, ctx=ext, errStr=errorStr))


class NewYearConvertResourcesProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self, fromResourceType, fromValue, toResourceType, toValue):
        confirmators = [plugins.AsyncDialogConfirmator(showResourcesConvertDialog, fromResourceType, fromValue, toResourceType, toValue)]
        super(NewYearConvertResourcesProcessor, self).__init__(confirmators)
        self.__fromResourceType = fromResourceType
        self.__fromValue = fromValue
        self.__toResourceType = toResourceType
        self.__toValue = toValue

    def _successHandler(self, code, ctx=None):
        serviceChannel = self.__systemMessages.proto.serviceChannel
        serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.NY_RESOURCES_CONVERTED_MESSAGE, auxData={'resourceType': self.__fromResourceType,
         'value': self.__fromValue,
         'exchangeType': 'decrease'})
        serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.NY_RESOURCES_CONVERTED_MESSAGE, auxData={'resourceType': self.__toResourceType,
         'value': self.__toValue,
         'exchangeType': 'increase'})
        return makeSuccess(userMsg='', auxData=ctx)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/convertingResources/error', type=SM_TYPE.ErrorSimple)

    def _request(self, callback):
        self._festivityFactory.getProcessor().convertResources(NY_CURRENCY_NAME_TO_IDX.get(self.__fromResourceType), NY_CURRENCY_NAME_TO_IDX.get(self.__toResourceType), self.__fromValue, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class BuyCollectionProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, collectionID, window):
        confirmators = [plugins.AsyncDialogConfirmator(showBuyDialog, window)]
        super(BuyCollectionProcessor, self).__init__(confirmators)
        self.__collectionID = collectionID

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/buyCollection/server_error')

    def _successHandler(self, code, ctx=None):
        year, collectionStr = getCollectionByIntID(self.__collectionID)
        collection = backport.text(R.strings.ny.settings.dyn(collectionStr)())
        msgId = R.strings.ny.systemMessage.infoCollection()
        year = backport.text(R.strings.ny.systemMessage.dyn(year)())
        msg = backport.text(msgId, collection=collection, year=year)
        return makeSuccess(userMsg=msg, auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to buy collection:(collectionID - %s)', self.__collectionID)
        self._festivityFactory.getProcessor().buyCollection(self.__collectionID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class RerollCelebrityQuestProcessor(Processor):
    _CUSTOM_ERRORS_MAP = {'No available rerolls': 'noRerolls'}
    _IS_ADDITIONAL_TO_GUEST_MAP = {False: GuestsQuestsTokens.GUEST_M,
     True: GuestsQuestsTokens.GUEST_A}
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, questID):
        super(RerollCelebrityQuestProcessor, self).__init__()
        self.__questID = questID
        self.addPlugins([_CelebrityQuestLockedByVehicleValidator()])

    def _errorHandler(self, code, errStr='', ctx=None):
        clientErrKey = ''
        for errorMarker, errKey in self._CUSTOM_ERRORS_MAP.iteritems():
            if errStr.startswith(errorMarker):
                clientErrKey = errKey
                break

        if clientErrKey:
            errorStr = backport.text(R.strings.system_messages.newYear.rerollCelebrityQuest.server_error.dyn(clientErrKey)())
        else:
            errorStr = backport.text(R.strings.system_messages.newYear.rerollCelebrityQuest.server_error())
        return makeError(errorStr, msgType=SM_TYPE.Error, msgPriority=NotificationPriorityLevel.MEDIUM, auxData={'clientErrKey': clientErrKey})

    def _successHandler(self, code, ctx=None):
        questType = CelebrityQuestTokenParts.getTypeFromFullQuestID(self.__questID)
        isAdditional = CelebrityQuestTokenParts.isAddQuestID(self.__questID)
        guest = self._IS_ADDITIONAL_TO_GUEST_MAP.get(isAdditional, GuestsQuestsTokens.GUEST_A)
        text = backport.text(R.strings.system_messages.newYear.rerollCelebrityQuest.dyn(guest).dyn(questType)())
        return makeSuccess(userMsg=text, msgType=SM_TYPE.Information, msgPriority=NotificationPriorityLevel.MEDIUM, auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to reroll celebrity quest: (questID - %s)', self.__questID)
        self._festivityFactory.getProcessor().rerollCelebrityQuest(self.__questID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class ResetLootboxStatisticsProcessor(Processor):
    __festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, boxID):
        super(ResetLootboxStatisticsProcessor, self).__init__([self.__buildConfirmator()])
        self.__boxID = boxID

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/resetLootboxStatistics/server_error', type=SM_TYPE.NewYearLootboxResetStatsError)

    def _request(self, callback):
        self.__festivityFactory.getProcessor().resetLootboxStatistics(self.__boxID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    @staticmethod
    def __buildConfirmator():
        builder = ConfirmCancelDialogBuilder()
        builder.setLayer(WindowLayer.OVERLAY)
        builder.setTitle(backport.text(R.strings.ny.confirmResetLootboxStatistics.title()))
        builder.setDescription(backport.text(R.strings.ny.confirmResetLootboxStatistics.description()))
        builder.setConfirmButtonLabel(R.strings.ny.confirmResetLootboxStatistics.submit())
        builder.setCancelButtonLabel(R.strings.ny.confirmResetLootboxStatistics.cancel())
        return plugins.AsyncDialogConfirmator(dialogs.showSimple, builder.build())


class NYSetHangarNameProcessor(Processor):
    __festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, cityTitleIdx, cityDesrictionIdx):
        super(NYSetHangarNameProcessor, self).__init__()
        self.__titleIdx = cityTitleIdx
        self.__descriptionIdx = cityDesrictionIdx

    def _request(self, callback):
        self.__festivityFactory.getProcessor().setHangarName(self.__titleIdx, self.__descriptionIdx, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class _NyBuyProcessor(Processor):

    def _errorHandler(self, code, errStr='', ctx=None):
        if code == AccountCommands.RES_CENTER_DISCONNECTED:
            errStr = 'server_error_centerDown'
        elif 'Insufficient amount' in errStr:
            errStr = 'not_enough_resource'
        else:
            errStr = 'server_error'
        msg = 'newYear/buying/errors/{}'.format(errStr)
        return makeI18nError(sysMsgKey=msg, auxData={'errStr': errStr})


class BuyMarketplaceItemProcessor(_NyBuyProcessor):
    __systemMessages = dependency.descriptor(ISystemMessages)
    _festivityFactory = dependency.descriptor(IFestivityFactory)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, item, categoryID, itemID, resourceID, dialog, parent=None):
        confirmators = [plugins.AsyncDialogConfirmator(showFullscreenConfirmDialog, dialog, parent), CollectionBoughtValidator(item)]
        super(BuyMarketplaceItemProcessor, self).__init__(confirmators)
        collectionDistributions = self._itemsCache.items.festivity.getCollectionDistributions()
        self.__categoryID = categoryID
        self.__itemID = itemID
        self.__resourceID = NY_CURRENCY_NAME_TO_IDX.get(resourceID)
        self.__price = item.getTotalPrice(collectionDistributions, bonusChecker)

    def _errorHandler(self, code, errStr='', ctx=None):
        resRoot = R.strings.system_messages.newYear.marketplace.errors
        if 'Collection already bought' in errStr:
            msg = resRoot.collection_already_bought()
        else:
            msg = resRoot.server_error()
        return makeError(backport.text(msg), msgType=SM_TYPE.ErrorSimple)

    def _successHandler(self, code, ctx=None):
        serviceChannel = self.__systemMessages.proto.serviceChannel
        serviceChannel.pushClientMessage('', msgType=SCH_CLIENT_MSG_TYPE.NY_CURRENCY_FINANCIAL_OPERATION_MESSAGE, auxData={'itemBought': backport.text(R.strings.system_messages.newYear.marketplace.collectionBought()),
         'price': self.__price,
         'resourceType': NY_CURRENCY_IDX_TO_NAME.get(self.__resourceID)})
        serviceChannel.pushClientMessage('', msgType=SCH_CLIENT_MSG_TYPE.NY_COLLECTION_REWARD_MESSAGE, auxData=ctx)
        return makeSuccess(userMsg='', auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to buy collection:(categoryID - %s, itemID - %s, resourceID - %s)', self.__categoryID, self.__itemID, self.__resourceID)
        self._festivityFactory.getProcessor().buyMarketplaceItem(self.__categoryID, self.__itemID, self.__resourceID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class BuyCelebrityQuestProcessor(_NyBuyProcessor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, guestName, questIndex, dialog, parent=None):
        confirmators = [plugins.AsyncDialogConfirmator(showFullscreenConfirmDialog, dialog, parent)]
        super(BuyCelebrityQuestProcessor, self).__init__(confirmators)
        self.__guestName = guestName
        self.__questIndex = questIndex

    def _successHandler(self, code, ctx=None):
        msg = ''
        return makeSuccess(userMsg=msg, auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to buy quest:(guestName - %s, questIndex - %s)', self.__guestName, self.__questIndex)
        self._festivityFactory.getProcessor().buyCelebrityQuest(self.__guestName, self.__questIndex, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class ApplyNyCoinProcessor(LootBoxOpenProcessor):

    def _errorHandler(self, code, errStr='', ctx=None):
        defaultKey = 'newYear/coin23/apply/server_error'
        return makeI18nError('/'.join((defaultKey, errStr)), defaultKey)


class BuyNyCoinProcessor(_NyBuyProcessor):
    _systemMessages = dependency.descriptor(ISystemMessages)
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, resourceType, amount):
        price = amount * getCoinPrice()
        confirmators = [ResourceTypeValidator(resourceType), BuyCoinsCountValidator(amount), ResourceEnoughValidator(resourceType, price)]
        super(BuyNyCoinProcessor, self).__init__(confirmators)
        self.__resourceID = NY_CURRENCY_NAME_TO_IDX.get(resourceType)
        self.__amount = amount
        self.__price = price

    def _successHandler(self, code, ctx=None):
        serviceChannel = self._systemMessages.proto.serviceChannel
        serviceChannel.pushClientMessage('', msgType=SCH_CLIENT_MSG_TYPE.NY_CURRENCY_FINANCIAL_OPERATION_MESSAGE, auxData={'itemBought': backport.text(R.strings.system_messages.newYear.giftMachine.tokenBought(), count=self.__amount),
         'price': self.__price,
         'resourceType': NY_CURRENCY_IDX_TO_NAME.get(self.__resourceID)})
        return makeSuccess('')

    def _errorHandler(self, code, errStr='', ctx=None):
        if code == AccountCommands.RES_CENTER_DISCONNECTED:
            errStr = 'server_error_centerDown'
        elif 'Insufficient amount' in errStr:
            errStr = 'not_enough_resource'
        elif 'invalid coins count' in errStr:
            errStr = 'invalid_coins_count'
        elif 'invalid resource type' in errStr:
            errStr = 'invalid_resource_type'
        else:
            errStr = 'server_error'
        msg = 'newYear/coin23/buying/errors/{}'.format(errStr)
        return makeI18nError(sysMsgKey=msg, auxData={'errStr': errStr})

    def _request(self, callback):
        _logger.debug('Make server request to buy nyCoins:(resourceType - %s, amount - %s)', self.__resourceID, self.__amount)
        self._festivityFactory.getProcessor().buyNyCoins(self.__resourceID, self.__amount, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class BuyObjectLevel(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, objectName, dialog=None, parent=None):
        confirmators = None
        if dialog is not None:
            confirmators = [plugins.AsyncDialogConfirmator(showFullscreenConfirmDialog, dialog, parent)]
        super(BuyObjectLevel, self).__init__(confirmators)
        self.__objectName = objectName
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/objectLevelUp/error')

    def _successHandler(self, code, ctx=None):
        msg = ''
        return makeSuccess(userMsg=msg, auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to upgrade customization object:(objectName - %s)', self.__objectName)
        self._festivityFactory.getProcessor().buyObjectLevel(self.__objectName, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class ManualCollectingResourcesProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self):
        super(ManualCollectingResourcesProcessor, self).__init__()
        self.__resources = {}
        collectingDescr = getNextCollectingDescr()
        if collectingDescr is not None:
            self.__resources = collectingDescr.getResources()
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/collectingResources/server_error/common')

    def _successHandler(self, code, ctx=None):
        serviceChannel = self.__systemMessages.proto.serviceChannel
        serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.NY_MANUAL_COLLECTING_MESSAGE, auxData={'resources': self.__resources})
        return makeSuccess(auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to manual collect resources')
        self._festivityFactory.getProcessor().manualCollectResources(lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class AutoCollectingResourcesProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self, state, parent=None):
        confirmators = []
        if state:
            confirmators.append(plugins.AsyncDialogConfirmator(showSetAutoCollectingDialog, parent=parent))
        super(AutoCollectingResourcesProcessor, self).__init__(confirmators)
        self.__state = state
        self.__cooldownBeforeRequest = None
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        msg = R.strings.system_messages.newYear.collectingResources.server_error.common()
        return makeError(backport.text(msg))

    def _successHandler(self, code, ctx=None):
        serviceChannel = self.__systemMessages.proto.serviceChannel
        serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.NY_AUTO_COLLECTING_ACTIVATE_MESSAGE, auxData={'state': self.__state,
         'cooldown': self.__cooldownBeforeRequest})
        return makeSuccess(auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to set auto collecting')
        self.__cooldownBeforeRequest = getCollectingCooldownTime()
        self._festivityFactory.getProcessor().setAutoCollectingResources(int(self.__state), lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class BuyToyProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __msgTypes = {Currency.CREDITS: SM_TYPE.NyBuyToyCredits,
     Currency.GOLD: SM_TYPE.NyBuyToyGold}

    def __init__(self, toyID, slotID, parent=None):
        confirmators = [plugins.AsyncDialogConfirmator(showCustomizationBuyDialog, parent=parent, toyID=toyID)]
        super(BuyToyProcessor, self).__init__(confirmators)
        self.__toyID = toyID
        self.__slotID = slotID
        self.__price = getToyPrice(self.__toyID)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/buyToy/server_error')

    def _successHandler(self, code, ctx=None):
        serviceChannel = self.__systemMessages.proto.serviceChannel
        rBase = R.strings.system_messages.newYear.buyToy
        currency, value = first(self.__price.iteritems(), (Currency.GOLD, 0))
        toyInfo = NewYearCurrentToyInfo(self.__toyID)
        if currency == Currency.GOLD:
            msgType = SM_TYPE.NyBuyToyGold
        else:
            msgType = SM_TYPE.NyBuyToyCredits
        serviceChannel.pushClientSysMessage(backport.text(rBase.text(), toy_name=backport.text(toyInfo.getName())), msgType=msgType, messageData={'spent_text': backport.text(rBase.dyn(currency)(), value=value)})
        return makeSuccess(auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to buy toy')
        self._festivityFactory.getProcessor().buyToy(self.__toyID, self.__slotID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class StrokeDogProcessor(Processor):
    __festivityFactory = dependency.descriptor(IFestivityFactory)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/strokeDog/server_error')

    def _successHandler(self, code, ctx=None):
        if ctx is not None:
            self.__systemMessages.proto.serviceChannel.pushClientMessage('', SCH_CLIENT_MSG_TYPE.NY_STROKE_DOG_MESSAGE, auxData={'resources': ctx})
        return makeSuccess(auxData=ctx)

    def _request(self, callback):
        self.__festivityFactory.getProcessor().strokeDog(lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class PiggyBankRewardsProcessor(Processor):
    __festivityFactory = dependency.descriptor(IFestivityFactory)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/piggyBank/server_error')

    def _request(self, callback):
        self.__festivityFactory.getProcessor().getNYPiggyBankRewards(lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isCelebrityQuestsRerollLockedByVehicle(itemsCache=None):
    levelsRange = range(CELEBRITY_LOCK_VEHICLE_MIN_LEVEL, MAX_VEHICLE_LEVEL + 1)
    criteria = REQ_CRITERIA.VEHICLE.IS_IN_BATTLE | REQ_CRITERIA.VEHICLE.LEVELS(levelsRange)
    for vehicle in itemsCache.items.getVehicles(criteria).values():
        if vehicle.typeOfLockingArena in CELEBRITY_LOCK_ARENA_BONUS_TYPES:
            return True

    return False


class _CelebrityQuestLockedByVehicleValidator(SyncValidator):

    def _validate(self):
        return plugins.makeError('locked_by_vehicle') if isCelebrityQuestsRerollLockedByVehicle() else plugins.makeSuccess()


class CollectionBoughtValidator(SyncValidator):

    def __init__(self, item, isEnabled=True):
        super(CollectionBoughtValidator, self).__init__(isEnabled)
        self._item = item

    def _validate(self):
        return plugins.makeError('Collection already bought') if isCollectionItemReceived(self._item) else plugins.makeSuccess()


class BuyItemValidator(SyncValidator):

    def __init__(self, item, resourceID, isEnabled=True):
        super(BuyItemValidator, self).__init__(isEnabled)
        self._item = item
        self._resourceID = resourceID

    @dependency.replace_none_kwargs(nyController=INewYearController, itemsCache=IItemsCache)
    def _validate(self, nyController=None, itemsCache=None):
        collectionDistributions = itemsCache.items.festivity.getCollectionDistributions()
        priceWithDiscount = self._item.getTotalPrice(collectionDistributions, bonusChecker)
        balance = nyController.currencies.getResouceBalance(self._resourceID)
        return plugins.makeError('not_enough_resource') if priceWithDiscount > balance else plugins.makeSuccess()


class ResourceTypeValidator(SyncValidator):

    def __init__(self, resourceID, isEnabled=True):
        super(ResourceTypeValidator, self).__init__(isEnabled)
        self.__resourceID = resourceID

    def _validate(self):
        return plugins.makeSuccess() if self.__resourceID in NyCurrency.ALL else plugins.makeError('invalid resource type')


class BuyCoinsCountValidator(SyncValidator):

    def __init__(self, amount, isEnabled=True):
        super(BuyCoinsCountValidator, self).__init__(isEnabled)
        self.__amount = amount

    def _validate(self):
        return plugins.makeSuccess() if self.__amount > 0 else plugins.makeError('invalid coins count')


class ResourceEnoughValidator(SyncValidator):

    def __init__(self, resourceID, price, isEnabled=True):
        super(ResourceEnoughValidator, self).__init__(isEnabled)
        self.__resourceID = resourceID
        self.__price = price

    @dependency.replace_none_kwargs(nyController=INewYearController)
    def _validate(self, nyController=None):
        balance = nyController.currencies.getResouceBalance(self.__resourceID)
        return plugins.makeSuccess() if balance >= self.__price else plugins.makeError('Insufficient amount')
