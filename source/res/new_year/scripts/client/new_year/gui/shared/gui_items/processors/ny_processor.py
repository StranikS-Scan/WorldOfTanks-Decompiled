# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/shared/gui_items/processors/ny_processor.py
import logging
from functools import partial
import typing
import AccountCommands
from festivity.base import BaseFestivityProcessor
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.backport import getIntegralFormat
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.gf_builders import ConfirmCancelDialogBuilder
from gui.impl.dialogs.sub_views.common.simple_text import ImageSubstitution
from gui.impl.gen.view_models.views.dialogs.template_settings.default_dialog_template_settings import DisplayFlags
from gui.impl.gen import R
from gui.shared.gui_items.processors import Processor, makeError, plugins, makeSuccess
from gui.shared.gui_items.processors.plugins import MessageConfirmator
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency, time_utils
from new_year.gui.shared import event_dispatcher
from new_year.messenger.formatters.service_channel import NewYearInvoiceDataSubformatter
from new_year_common.items import new_year, collectibles
from new_year_common.items.components.ny_constants import ToySettings, YEARS, OBJECT_MAX_LEVEL
from new_year_common.items.new_year import getCollectionByIntID
from new_year.helpers.ny_helpers import getCurrentObjectLevel
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from new_year.helpers.server_settings import getNewYearMachineConfig
from new_year.skeletons.new_year import INewYearController
from new_year.gui.shared.ny_toy_info import NewYearCurrentToyInfo
from new_year.gui.impl.lobby.new_year.dialogs.dialogs import showBuyDialog
from skeletons.festivity_factory import IFestivityFactory
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger()
if typing.TYPE_CHECKING:
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper

class NewYearCommandsProcessor(BaseFestivityProcessor):

    def hangToy(self, toyID, slotID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_SLOT_FILL, (slotID, toyID), callback)

    def applyVariadicDiscount(self, goodiesIDs, discountIDs, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_SELECT_DISCOUNT, (goodiesIDs, discountIDs), callback)

    def breakToys(self, toys, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_BREAK_TOYS, (toys,), callback)

    def sendSeen(self, seenToys):
        self._perform(AccountCommands.CMD_NEW_YEAR_SEE_INVENTORY_TOYS, (seenToys,))

    def seenInCollection(self, seenToys):
        self._perform(AccountCommands.CMD_NEW_YEAR_SEE_COLLECTION_TOYS, (seenToys,))

    def viewAlbum(self, settingID, rank):
        self._perform(AccountCommands.CMD_NEW_YEAR_VIEW_ALBUM, (settingID, rank))

    def buyCollection(self, collectionID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_FILL_OLD_COLLECTION, (collectionID,), callback)

    def resetLootboxStatistics(self, boxID, callback=None):
        self._perform(AccountCommands.CMD_LOOTBOX_RESET_STATS, (boxID,), callback)

    def addToys(self, toysDict=None):
        if toysDict:
            toysToAdd = []
            for toyID, count in toysDict.iteritems():
                toysToAdd.extend([toyID] * count)

        else:
            toysToAdd = new_year.g_cache.toys.keys()
        self._perform(AccountCommands.CMD_NEW_YEAR_ADD_TOYS_DEV, (toysToAdd,))

    def addFragments(self, count=1000):
        self._perform(AccountCommands.CMD_NEW_YEAR_ADD_TOY_FRAGMENTS_DEV, (count,))

    def addOldToys(self, year, toysDict=None):
        yearStr = YEARS.getYearStrFromYearNum(year)
        if toysDict:
            toysToAdd = []
            for toyID, count in toysDict.iteritems():
                toysToAdd.extend([toyID] * count)

        else:
            toysToAdd = collectibles.g_cache[yearStr].toys
        self._perform(AccountCommands.CMD_NEW_YEAR_ADD_OLD_TOYS_DEV, (toysToAdd, yearStr))

    def buyMachineCoins(self, amount, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_BUY_MACHINE_COINS, (amount,), callback)

    def upgradeObjectLevel(self, objectName, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_UPGRADE_OBJECT_LEVEL, (objectName,), callback)

    def buyToy(self, toyID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_BUY_TOY, (toyID,), callback)


class ApplyVehicleDiscountProcessor(Processor):
    _CUSTOM_ERRORS_MAP = {'wrong variadicDiscountID': 'noDiscounts',
     'missing variadic discount': 'noDiscounts',
     'discount already exists': 'alreadyActive',
     'vehicle already in inventory': 'alreadyBought',
     'goodieID': 'noDiscountForVehicle',
     'the length': 'wrongData'}
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, goodiesIDs, discountIDs):
        super(ApplyVehicleDiscountProcessor, self).__init__()
        self.__goodiesIDs = goodiesIDs
        self.__discountIDs = discountIDs

    def _errorHandler(self, code, errStr='', ctx=None):
        clientErrKey = ''
        for errorMarker, errKey in self._CUSTOM_ERRORS_MAP.iteritems():
            if errStr.startswith(errorMarker):
                clientErrKey = errKey
                break

        return makeError(backport.text(R.strings.ny.systemMessage.applyVehicleDiscount.server_error.dyn(clientErrKey)())) if clientErrKey else makeError(backport.text(R.strings.ny.systemMessage.applyVehicleDiscount.server_error()))

    def _request(self, callback):
        _logger.debug('Make server request to apply vehcile discount goodiesID: %s, discountID: %s', self.__goodiesIDs, self.__discountIDs)
        self._festivityFactory.getProcessor().applyVariadicDiscount(self.__goodiesIDs, self.__discountIDs, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class NewYearBreakToysProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)
    _itemsCache = dependency.descriptor(IItemsCache)
    _MIN_COUNT_TO_CONFIRM_DECAY = 3

    def __init__(self, toysToBreak, expectedShardsCount, needConfirm=True, parent=None):
        manyToys = len(toysToBreak) >= self._MIN_COUNT_TO_CONFIRM_DECAY
        unusedToys = self.__hasUnusedToys(toysToBreak)
        confirmator = None
        if needConfirm:
            if unusedToys:
                confirmator = [self.__buildUnusedConfirmator(expectedShardsCount, parent)]
            elif manyToys:
                confirmator = [self.__buildConfirmator(expectedShardsCount, parent)]
        super(NewYearBreakToysProcessor, self).__init__(confirmator)
        self.__toysToBreak = self.__prepareToysServerFormat(toysToBreak)
        self.__expectedShardsCount = expectedShardsCount
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeError(backport.text(R.strings.ny.systemMessage.breakToys.server_error()))

    def _successHandler(self, code, ctx=None):
        str = NewYearInvoiceDataSubformatter.getNyFragmentsString(self.__expectedShardsCount)
        result = makeSuccess(str, msgType=SM_TYPE.Information)
        return result

    def _request(self, callback):
        self._festivityFactory.getProcessor().breakToys(self.__toysToBreak, lambda resultID, errorStr, ext: self._response(resultID, callback, ctx=ext, errStr=errorStr))

    @staticmethod
    def __buildConfirmator(expectedShardsCount, parent):
        textPath = R.strings.ny.confirmBreakToys
        title = backport.text(textPath.title(), count=getIntegralFormat(expectedShardsCount), icon='%(icon)s')
        marginTop = 4
        marginRight = -6
        marginLeft = -6
        message = textPath.message()
        shardImage = ImageSubstitution(R.images.new_year.gui.maps.icons.newYear.shards.c_64x64(), 'icon', marginTop, marginRight, 0, marginLeft)
        builder = ConfirmCancelDialogBuilder()
        builder.setTitle(title, [shardImage])
        builder.setDescription(message, [shardImage])
        builder.setConfirmButtonLabel(textPath.submit())
        builder.setCancelButtonLabel(textPath.cancel())
        builder.setBlur(True)
        return plugins.AsyncDialogConfirmator(dialogs.showSimple, builder.build())

    @staticmethod
    def __buildUnusedConfirmator(expectedShardsCount, parent):
        textPath = R.strings.ny.confirmBreakToys
        title = textPath.atmosphereBonusTitle()
        marginTop = -14
        marginRight = -8
        marginLeft = -8
        message = backport.text(textPath.atmosphereBonusMessage(), count=getIntegralFormat(expectedShardsCount), icon='%(icon)s')
        shardImage = ImageSubstitution(R.images.new_year.gui.maps.icons.newYear.shards.c_48x48(), 'icon', marginTop, marginRight, 0, marginLeft)
        builder = ConfirmCancelDialogBuilder()
        builder.setDisplayFlags(DisplayFlags.RESPONSIVEHEADER.value)
        builder.setTitle(title, [shardImage])
        builder.setDescription(message, [shardImage])
        builder.setConfirmButtonLabel(textPath.submit())
        builder.setCancelButtonLabel(textPath.cancel())
        builder.setBlur(True)
        return plugins.AsyncDialogConfirmator(dialogs.showSimple, builder.build())

    def __hasUnusedToys(self, toys):
        controller = self._festivityFactory.getController()
        if controller.isMaxAtmosphereLevel():
            return False
        slotsData = self._itemsCache.items.festivity.getSlots()
        slots = controller.getSlotDescrs()
        toyTypes = {toyDescr.type for toyDescr in [ controller.getToyDescr(toyID) for toyID in toys.keys() ]}
        slotTypes = {slot.type for slot, slotData in zip(slots, slotsData) if slotData == -1}
        return len(toyTypes.intersection(slotTypes)) > 0

    def __prepareToysServerFormat(self, toysToBreak):
        toysToBreakServerFormat = []
        for toyID, countData in toysToBreak.iteritems():
            toysToBreakServerFormat.extend((toyID, countData))

        return toysToBreakServerFormat


class HangToyProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, toyID, slotID):
        super(HangToyProcessor, self).__init__()
        self.__toyID = toyID
        self.__slotID = slotID

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeError(backport.text(R.strings.ny.systemMessage.hangToy.server_error()))

    def _request(self, callback):
        self._festivityFactory.getProcessor().hangToy(self.__toyID, self.__slotID, lambda resultID, errorStr, ext: self._response(resultID, callback, ctx=ext, errStr=errorStr))


class BuyCollectionProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, collectionID, window):
        confirmators = [plugins.AsyncDialogConfirmator(showBuyDialog, window)]
        super(BuyCollectionProcessor, self).__init__(confirmators)
        self.__collectionID = collectionID

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeError(backport.text(R.strings.ny.systemMessage.buyCollection.server_error()))

    def _successHandler(self, code, ctx=None):
        year, collectionStr = getCollectionByIntID(self.__collectionID)
        collection = backport.text(R.strings.ny.settings.dyn(collectionStr)())
        if collectionStr == ToySettings.MEGA_TOYS:
            msgId = R.strings.ny.systemMessage.infoMegaCollection()
        else:
            msgId = R.strings.ny.systemMessage.infoCollection()
        year = backport.text(R.strings.ny.systemMessage.dyn(year)())
        msg = backport.text(msgId, collection=collection, year=year)
        return makeSuccess(userMsg=msg, auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to buy collection:(collectionID - %s)', self.__collectionID)
        self._festivityFactory.getProcessor().buyCollection(self.__collectionID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class BuyMachineCoinsProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, count):
        super(BuyMachineCoinsProcessor, self).__init__()
        self.__count = count

    def _successHandler(self, code, ctx=None):
        machineConfig = getNewYearMachineConfig()
        msg = backport.text(R.strings.ny.notification.machine.trade.text(), mandarinsCount=machineConfig.getCoinPrice() * self.__count, machineCount=self.__count)
        header = backport.text(R.strings.ny.notification.machine.trade.header())
        return makeSuccess(userMsg=msg, msgType=SM_TYPE.NewYearBuyMachineTokens, msgData={'header': header}, msgPriority=NotificationPriorityLevel.MEDIUM)

    def _request(self, callback):
        _logger.debug('Make server request to buy machine coins count=%d', self.__count)
        self._festivityFactory.getProcessor().buyMachineCoins(self.__count, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class UpgradeCustomizationObjectLevel(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, customizationObject):
        super(UpgradeCustomizationObjectLevel, self).__init__()
        self.__customizationObject = customizationObject

    def _errorHandler(self, code, errStr='', ctx=None):
        customizationZone = backport.text(R.strings.ny.customizationZones.notification.dyn(self.__customizationObject)())
        msg = backport.text(R.strings.ny.systemMessage.customizationZones.server_error(), customizationZone=customizationZone)
        header = backport.text(R.strings.ny.systemMessage.customizationZones.server_error.header())
        return makeError(userMsg=msg, msgType=SM_TYPE.ErrorHeader, msgData={'header': header}, msgPriority=NotificationPriorityLevel.HIGH)

    def _successHandler(self, code, ctx=None):
        currentLevel = getCurrentObjectLevel(self.__customizationObject)
        if currentLevel == OBJECT_MAX_LEVEL:
            msgId = R.strings.ny.customizationZones.notification.maxLevel.text()
        else:
            msgId = R.strings.ny.customizationZones.notification.text()
        customizationZone = backport.text(R.strings.ny.customizationZones.notification.dyn(self.__customizationObject)())
        msg = backport.text(msgId, currentLevel=currentLevel, toyCount=self._getToysCount(currentLevel))
        header = backport.text(R.strings.ny.customizationZones.notification.header(), customizationZone=customizationZone)
        return makeSuccess(userMsg=msg, msgType=SM_TYPE.InformationHeader, msgData={'header': header}, msgPriority=NotificationPriorityLevel.MEDIUM)

    def _request(self, callback):
        _logger.debug('Make server request to upgrade customization object - %s', self.__customizationObject)
        self._festivityFactory.getProcessor().upgradeObjectLevel(self.__customizationObject, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _getToysCount(self, currentLevel):
        return len(NewYearAtmospherePresenter.getNewYearLevelToys(self.__customizationObject, currentLevel))


class _BuyToyConfirmator(MessageConfirmator):

    def __init__(self, toyID):
        super(_BuyToyConfirmator, self).__init__(None, True)
        self.__toyID = toyID
        return

    def _gfMakeMeta(self):
        return partial(event_dispatcher.showNYBuyToyDialog, self.__toyID)


class BuyToyProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, toyID):
        super(BuyToyProcessor, self).__init__()
        self.__toyID = toyID
        self.addPlugins((_BuyToyConfirmator(self.__toyID),))

    def _errorHandler(self, code, errStr='', ctx=None):
        msg = backport.text(R.strings.ny.notification.racoon.server_error.text())
        header = backport.text(R.strings.ny.notification.racoon.server_error.header())
        return makeError(userMsg=msg, msgType=SM_TYPE.ErrorHeader, msgData={'header': header}, msgPriority=NotificationPriorityLevel.HIGH)

    def _successHandler(self, code, ctx=None):
        toy = self._nyController.getToyByID(int(self.__toyID))
        msg = backport.text(R.strings.ny.notification.racoon.buyToy.text(), toyName=backport.text(NewYearCurrentToyInfo(int(self.__toyID)).getName()), time=time_utils.getDateTimeInLocal(time_utils.getCurrentTimestamp()).strftime('%d.%m.%y %H:%M:%S'), goldCount=toy.getPrice().gold)
        return makeSuccess(userMsg=msg, msgType=SM_TYPE.FinancialTransactionWithGold, msgData={'header': backport.text(R.strings.ny.notification.racoon.buyToy.header())}, msgPriority=NotificationPriorityLevel.MEDIUM)

    def _request(self, callback):
        _logger.debug('Make server request to buy toy by ID - %s', self.__toyID)
        self._festivityFactory.getProcessor().buyToy(self.__toyID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
