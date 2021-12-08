# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_processor.py
import logging
import typing
import AccountCommands
from constants import MAX_VEHICLE_LEVEL
from festivity.base import BaseFestivityProcessor
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.gf_builders import ConfirmCancelDialogBuilder
from gui.impl.dialogs.sub_views.common.simple_text import ImageSubstitution
from gui.impl.lobby.new_year.dialogs.dialogs import showBuyDialog
from gui.impl.gen import R
from gui.impl.lobby.new_year.dialogs.reset_loot_box_statistics_builder import ResetLootBoxStatisticsBuilder
from gui.shared.gui_items.processors.plugins import SyncValidator
from gui.shared.utils.requesters import REQ_CRITERIA
from items import new_year
from helpers import dependency
from gui.shared.gui_items.processors import Processor, makeI18nError, plugins, makeSuccess
from items.components.ny_constants import CELEBRITY_LOCK_VEHICLE_MIN_LEVEL, CELEBRITY_LOCK_ARENA_BONUS_TYPES, ToySettings, FillerState
from items.new_year import getCollectionByIntID
from skeletons.festivity_factory import IFestivityFactory
from skeletons.gui.shared import IItemsCache
from shared_utils import findFirst
from skeletons.new_year import INewYearCraftMachineController
_logger = logging.getLogger()
if typing.TYPE_CHECKING:
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogWindowWrapper

class NewYearCommandsProcessor(BaseFestivityProcessor):

    def hangToy(self, toyID, slotID, toyUsage, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_SLOT_FILL, (slotID, toyID, toyUsage), callback)

    def applyVariadicDiscount(self, goodiesID, discountID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_SELECT_DISCOUNT, (goodiesID, discountID), callback)

    def craftToy(self, toyTypeID, settingID, rank, filler, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_CRAFT, (toyTypeID,
         settingID,
         rank,
         filler), callback)

    def breakToys(self, toys, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_BREAK_TOYS, (toys,), callback)

    def sendSeen(self, seenToys):
        self._perform(AccountCommands.CMD_NEW_YEAR_SEE_INVENTORY_TOYS, (seenToys,))

    def seenInCollection(self, seenToys):
        self._perform(AccountCommands.CMD_NEW_YEAR_SEE_COLLECTION_TOYS, (seenToys,))

    def viewAlbum(self, settingID, rank):
        self._perform(AccountCommands.CMD_NEW_YEAR_VIEW_ALBUM, (settingID, rank))

    def buyToy(self, toyID, year, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_CRAFT_OLD_TOYS, (toyID, year), callback)

    def buyCollection(self, collectionID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_FILL_OLD_COLLECTION, (collectionID,), callback)

    def setVehicleBranch(self, vehicleInvID, slotID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_SET_NY_VEHICLE, (vehicleInvID, slotID), callback)

    def setVehicleBranchSlotBonus(self, slotID, choiceID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_CHOOSE_SLOT_BONUS, (slotID, choiceID), callback)

    def simplifyCelebrityQuest(self, level, questID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_SIMPLIFY_CELEBRITY_QUEST, (level, questID), callback)

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


class CraftProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)
    __craftCtrl = dependency.descriptor(INewYearCraftMachineController)

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
        if self.__filler == FillerState.USE_SHARDS.value:
            msg = backport.text(R.strings.ny.systemMessage.useChardsToFiller(), shardsCount=self.__craftCtrl.fillerShardsCost)
        return makeSuccess(userMsg=msg, auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to craft toyTypeID: %s, settingID: %s, rank: %s', self.__toyTypeID, self.__settingID, self.__rankID)
        self._festivityFactory.getProcessor().craftToy(self.__toyTypeID, self.__settingID, self.__rankID, self.__filler, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class ApplyVehicleDiscountProcessor(Processor):
    _CUSTOM_ERRORS_MAP = {'wrong variadicDiscountID': 'noDiscounts',
     'missing variadic discount': 'noDiscounts',
     'discount already exists': 'alreadyActive',
     'vehicle already in inventory': 'alreadyBought',
     'goodieID': 'noDiscountForVehicle'}
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, goodiesID, discountID):
        super(ApplyVehicleDiscountProcessor, self).__init__()
        self.__goodiesID = goodiesID
        self.__discountID = discountID

    def _errorHandler(self, code, errStr='', ctx=None):
        clientErrKey = ''
        for errorMarker, errKey in self._CUSTOM_ERRORS_MAP.iteritems():
            if errStr.startswith(errorMarker):
                clientErrKey = errKey
                break

        defaultKey = 'newYear/applyVehicleDiscount/server_error'
        return makeI18nError('/'.join((defaultKey, clientErrKey)), defaultKey)

    def _request(self, callback):
        _logger.debug('Make server request to apply vehcile discount goodiesID: %s, discountID: %s', self.__goodiesID, self.__discountID)
        self._festivityFactory.getProcessor().applyVariadicDiscount(self.__goodiesID, self.__discountID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class NewYearBreakToysProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)
    _MIN_COUNT_TO_CONFIRM_DECAY = 3

    def __init__(self, toysToBreak, expectedShardsCount, needConfirm=True, parent=None):
        isMaxAtmosphereLevel = self._festivityFactory.getController().isMaxAtmosphereLevel()
        isMegaToysToBreak = self.__containsMegaToys(toysToBreak)
        hasToysWithAtmosphereBonus = not isMaxAtmosphereLevel and self.__containsToysWithAtmosphereBonus(toysToBreak)
        manyToys = len(toysToBreak) >= self._MIN_COUNT_TO_CONFIRM_DECAY
        confirmator = None
        if needConfirm and (manyToys or isMegaToysToBreak or hasToysWithAtmosphereBonus):
            confirmator = [self.__buildConfirmator(expectedShardsCount, parent, isMegaToysToBreak, hasToysWithAtmosphereBonus)]
        super(NewYearBreakToysProcessor, self).__init__(confirmator)
        self.__toysToBreak = self.__prepareToysServerFormat(toysToBreak)
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/breakToys/server_error')

    def _request(self, callback):
        self._festivityFactory.getProcessor().breakToys(self.__toysToBreak, lambda resultID, errorStr, ext: self._response(resultID, callback, ctx=ext, errStr=errorStr))

    @staticmethod
    def __buildConfirmator(expectedShardsCount, parent, isMegaToysToBreak, hasToysWithAtmosphereBonus):
        textPath = R.strings.ny.confirmBreakToys
        title = backport.text(textPath.title(), count=expectedShardsCount, icon='%(icon)s')
        marginTop = 4
        if hasToysWithAtmosphereBonus:
            title = textPath.atmosphereBonusTitle()
            message = backport.text(textPath.atmosphereBonusMessage(), count=expectedShardsCount, icon='%(icon)s')
            marginTop = -1
        elif isMegaToysToBreak:
            message = textPath.megaToysMessage()
        else:
            message = textPath.message()
        shardImage = ImageSubstitution(R.images.gui.maps.icons.newYear.shards.c_24x24(), 'icon', marginTop)
        builder = ConfirmCancelDialogBuilder()
        builder.setTitle(title, [shardImage])
        builder.setDescription(message, [shardImage])
        builder.setConfirmButtonLabel(textPath.submit())
        builder.setCancelButtonLabel(textPath.cancel())
        return plugins.AsyncDialogConfirmator(dialogs.showSimple, builder.build(withBlur=True))

    def __prepareToysServerFormat(self, toysToBreak):
        toysToBreakServerFormat = []
        for toyID, countData in toysToBreak.iteritems():
            countToBreak, pureCount = countData
            toysToBreakServerFormat.extend((toyID, countToBreak, pureCount))

        return toysToBreakServerFormat

    @staticmethod
    def __containsMegaToys(toysToBreak):
        for toyID in toysToBreak.iterkeys():
            toyDescr = new_year.g_cache.toys.get(toyID)
            if toyDescr is None:
                continue
            if toyDescr.isMegaToy():
                return True

        return False

    @staticmethod
    def __containsToysWithAtmosphereBonus(toysToBreak):
        return bool(findFirst(lambda t: t[1], toysToBreak.itervalues()))


class HangToyProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, toyID, slotID, toyUsage):
        super(HangToyProcessor, self).__init__()
        self.__toyID = toyID
        self.__slotID = slotID
        self.__toyUsage = toyUsage

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/hangToy/server_error')

    def _request(self, callback):
        self._festivityFactory.getProcessor().hangToy(self.__toyID, self.__slotID, self.__toyUsage, lambda resultID, errorStr, ext: self._response(resultID, callback, ctx=ext, errStr=errorStr))


class BuyToyProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, toyInfo, window):
        confirmators = [plugins.AsyncDialogConfirmator(showBuyDialog, window)]
        super(BuyToyProcessor, self).__init__(confirmators)
        self.__toy = toyInfo

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/buyMegaToy/server_error') if self.__toy.isMega() else makeI18nError('newYear/buyToy/server_error')

    def _successHandler(self, code, ctx=None):
        toyName = backport.text(self.__toy.getName())
        collection = backport.text(R.strings.ny.settings.dyn(self.__toy.getCollectionName())())
        year = backport.text(R.strings.ny.systemMessage.dyn(self.__toy.COLLECTION_NAME)())
        if not self.__toy.isMega():
            msgId = R.strings.ny.systemMessage.infoToy()
        else:
            msgId = R.strings.ny.systemMessage.infoMegaToy()
        msg = backport.text(msgId, toyName=toyName, collection=collection, year=year)
        return makeSuccess(userMsg=msg, auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to buy toy:(id - %s, year - %s)', self.__toy.getID(), self.__toy.COLLECTION_NAME)
        self._festivityFactory.getProcessor().buyToy(self.__toy.getID(), self.__toy.COLLECTION_NAME, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


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


class SimplifyCelebrityQuestProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, questID, level):
        super(SimplifyCelebrityQuestProcessor, self).__init__()
        self.__questID = questID
        self.__level = level
        self.addPlugins([_CelebrityQuestLockedByVehicleValidator()])

    def _request(self, callback):
        _logger.debug('Make server request to simplify celebrity quest: (questID - %s)', self.__questID)
        self._festivityFactory.getProcessor().simplifyCelebrityQuest(self.__level, self.__questID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


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
        builder = ResetLootBoxStatisticsBuilder()
        builder.setTitle(backport.text(R.strings.ny.confirmResetLootboxStatistics.title()))
        builder.setDescription(backport.text(R.strings.ny.confirmResetLootboxStatistics.description()))
        builder.setConfirmButtonLabel(R.strings.ny.confirmResetLootboxStatistics.submit())
        builder.setCancelButtonLabel(R.strings.ny.confirmResetLootboxStatistics.cancel())
        return plugins.AsyncDialogConfirmator(dialogs.showSimple, builder.build(withBlur=True))


class _CelebrityQuestLockedByVehicleValidator(SyncValidator):

    def _validate(self):
        return plugins.makeError('locked_by_vehicle') if isCelebrityQuestsSimplificationLocked() else plugins.makeSuccess()


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isCelebrityQuestsSimplificationLocked(itemsCache=None):
    levelsRange = range(CELEBRITY_LOCK_VEHICLE_MIN_LEVEL, MAX_VEHICLE_LEVEL + 1)
    criteria = REQ_CRITERIA.VEHICLE.IS_IN_BATTLE | REQ_CRITERIA.VEHICLE.LEVELS(levelsRange)
    for vehicle in itemsCache.items.getVehicles(criteria).values():
        if vehicle.typeOfLockingArena in CELEBRITY_LOCK_ARENA_BONUS_TYPES:
            return True

    return False
