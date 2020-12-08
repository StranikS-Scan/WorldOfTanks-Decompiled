# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_processor.py
import logging
import typing
import AccountCommands
from constants import MAX_VEHICLE_LEVEL
from festivity.base import BaseFestivityProcessor
from gui.impl import backport
from gui.impl.dialogs import dialogs
from gui.impl.dialogs.builders import InfoDialogBuilderEx
from gui.impl.gen import R
from gui.impl.wrappers.user_format_string_arg_model import UserFormatStringArgModel as FmtArgs
from gui.shared.formatters import icons, text_styles
from gui.shared.gui_items.processors.plugins import SyncValidator
from gui.shared.utils.requesters import REQ_CRITERIA
from items import new_year
from helpers import dependency
from gui.shared.gui_items.processors import Processor, makeI18nError, plugins, makeSuccess
from items.components.ny_constants import CELEBRITY_LOCK_VEHICLE_MIN_LEVEL, CELEBRITY_LOCK_ARENA_BONUS_TYPES, ToySettings
from items.new_year import getCollectionByIntID
from skeletons.festivity_factory import IFestivityFactory
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger()
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window

class NewYearCommandsProcessor(BaseFestivityProcessor):

    def hangToy(self, toyID, slotID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_SLOT_FILL, (slotID, toyID), callback)

    def applyVariadicDiscount(self, goodiesID, discountID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_SELECT_DISCOUNT, (goodiesID, discountID), callback)

    def craftToy(self, toyTypeID, settingID, rank, useFiller, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_CRAFT, (toyTypeID,
         settingID,
         rank,
         useFiller), callback)

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

    def addTalisman(self, talismanID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_ADD_TALISMAN, (talismanID,), callback)

    def getTalismanToy(self, talismanID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_TAKE_TALISMAN_BONUS, (talismanID,), callback)

    def setVehicleBranch(self, vehicleInvID, slotID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_SET_NY_VEHICLE, (vehicleInvID, slotID), callback)

    def setVehicleBranchSlotBonus(self, slotID, choiceID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_CHOOSE_SLOT_BONUS, (slotID, choiceID), callback)

    def setVehicleCamouflage(self, vehInvID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_SET_CAMOUFLAGE, (vehInvID,), callback)

    def simplifyCelebrityQuest(self, level, questID, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_SIMPLIFY_CELEBRITY_QUEST, (level, questID), callback)

    def changeTalismanBonusStage(self, nextStage, callback=None):
        self._perform(AccountCommands.CMD_NEW_YEAR_CHANGE_TALISMAN_BONUS_STAGE, (nextStage,), callback)

    def addToys(self, toysDict=None):
        if toysDict:
            toysToAdd = []
            for toyID, count in toysDict.iteritems():
                toysToAdd.extend([toyID] * count)

        else:
            toysToAdd = new_year.g_cache.toys.keys()
        self._perform(AccountCommands.CMD_NEW_YEAR_ADD_TOYS_DEV, (toysToAdd,))

    def resetNYDailyLimits(self):
        self._perform(AccountCommands.CMD_NEW_YEAR_RESET_LIMITS_DEV, ('',))

    def resetNYTalismans(self):
        self._perform(AccountCommands.CMD_NEW_YEAR_RESET_TALISMANS_DEV, ('',))


class CraftProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, toyTypeID, settingID, rank, useFiller):
        super(CraftProcessor, self).__init__()
        self.__toyTypeID = toyTypeID
        self.__settingID = settingID
        self.__rankID = rank
        self.__useFiller = useFiller

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/craftToy/server_error')

    def _request(self, callback):
        _logger.debug('Make server request to craft toyTypeID: %s, settingID: %s, rank: %s', self.__toyTypeID, self.__settingID, self.__rankID)
        self._festivityFactory.getProcessor().craftToy(self.__toyTypeID, self.__settingID, self.__rankID, self.__useFiller, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


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
    _lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self, toysToBreak, expectedShardsCount, needConfirm=True, parent=None):
        isMegaToysToBreak = self.__containsMegaToys(toysToBreak)
        toyDecayCostConfig = self._lobbyCtx.getServerSettings().getNewYearToyDecayCostConfig()
        threshold = toyDecayCostConfig.getMaxToyDecayCost()
        condition = (expectedShardsCount >= threshold or isMegaToysToBreak) and needConfirm
        confirmator = [self.__buildConfirmator(expectedShardsCount, parent, isMegaToysToBreak)] if condition else None
        super(NewYearBreakToysProcessor, self).__init__(confirmator)
        self.__toysToBreak = self.__prepareToysServerFormat(toysToBreak)
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/breakToys/server_error')

    def _request(self, callback):
        self._festivityFactory.getProcessor().breakToys(self.__toysToBreak, lambda resultID, errorStr, ext: self._response(resultID, callback, ctx=ext, errStr=errorStr))

    @staticmethod
    def __buildConfirmator(expectedShardsCount, parent, isMegaToysToBreak):
        formattedCount = '{}{}'.format(text_styles.grandTitle(backport.getIntegralFormat(expectedShardsCount)), icons.makeImageTag(backport.image(R.images.gui.maps.icons.new_year.icons.parts_24x24()), width=24, height=24, vSpace=1))
        message = 'megaToysMessage' if isMegaToysToBreak else ''
        builder = InfoDialogBuilderEx(customMessageSection=message)
        builder.setMessagesAndButtons(R.strings.ny.confirmBreakToys, buttons=R.strings.ny.confirmBreakToys)
        builder.setTitleArgs(fmtArgs=[FmtArgs(formattedCount, 'count', R.styles.GrandTitleTextStyle())])
        return plugins.AsyncDialogConfirmator(dialogs.showSimple, builder.build(parent))

    @staticmethod
    def __prepareToysServerFormat(toysToBreak):
        toysToBreakServerFormat = []
        for k, v in toysToBreak.iteritems():
            toysToBreakServerFormat.append(k)
            toysToBreakServerFormat.append(v)

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


class BuyToyProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, toyInfo, parent=None):
        confirmators = [plugins.AsyncDialogConfirmator(dialogs.newYearCollectionBuyItem, toyInfo, parent)]
        super(BuyToyProcessor, self).__init__(confirmators)
        self.__toy = toyInfo

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/buyMegaToy/server_error') if self.__toy.isMega() else makeI18nError('newYear/buyToy/server_error')

    def _successHandler(self, code, ctx=None):
        toyName = backport.text(self.__toy.getName())
        collection = backport.text(R.strings.ny.settingsWithCollection.dyn(self.__toy.getCollectionName())())
        year = backport.text(R.strings.ny.systemMessage.dyn(self.__toy.COLLECTION_NAME)())
        if not self.__toy.isMega():
            msgId = R.strings.ny.systemMessage.infoToy()
        else:
            msgId = R.strings.ny.systemMessage.infoMegaToy()
        msg = backport.text(msgId).format(toyname=toyName, ofcollection=collection, year=year)
        return makeSuccess(userMsg=msg, auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to buy toy:(id - %s, year - %s)', self.__toy.getID(), self.__toy.COLLECTION_NAME)
        self._festivityFactory.getProcessor().buyToy(self.__toy.getID(), self.__toy.COLLECTION_NAME, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class BuyCollectionProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, collectionID, parent=None):
        confirmators = [plugins.AsyncDialogConfirmator(dialogs.newYearBuyCollection, collectionID, parent)]
        super(BuyCollectionProcessor, self).__init__(confirmators)
        self.__collectionID = collectionID

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/buyCollection/server_error')

    def _successHandler(self, code, ctx=None):
        year, collectionStr = getCollectionByIntID(self.__collectionID)
        collection = backport.text(R.strings.ny.settingsWithCollection.dyn(collectionStr)())
        if collectionStr == ToySettings.MEGA_TOYS:
            msgId = R.strings.ny.systemMessage.infoMegaCollection()
        else:
            msgId = R.strings.ny.systemMessage.infoCollection()
        year = backport.text(R.strings.ny.systemMessage.dyn(year)())
        msg = backport.text(msgId).format(ofcollection=collection, year=year)
        return makeSuccess(userMsg=msg, auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to buy collection:(collectionID - %s)', self.__collectionID)
        self._festivityFactory.getProcessor().buyCollection(self.__collectionID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


class _TalismanProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, talismanSetting, confirmators):
        super(_TalismanProcessor, self).__init__(confirmators)
        talismans = self._nyController.getTalismans()
        self._talismanID = 0
        for talisman in talismans:
            if talisman.getSetting() == talismanSetting:
                self._talismanID = talisman.getID()
                break


class AddTalismanProcessor(_TalismanProcessor):

    def __init__(self, talismanSetting):
        confirmators = [plugins.AsyncDialogConfirmator(dialogs.showNYTalismanSelectConfirm, talismanSetting)]
        super(AddTalismanProcessor, self).__init__(talismanSetting, confirmators)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/addTalisman/server_error')

    def _request(self, callback):
        self._festivityFactory.getProcessor().addTalisman(self._talismanID, lambda resultID, errorStr, ext: self._response(resultID, callback, ctx=ext, errStr=errorStr))


class GetTalismanToyProcessor(_TalismanProcessor):

    def __init__(self, talismanSetting):
        super(GetTalismanToyProcessor, self).__init__(talismanSetting, [])

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/getTalismanToy/server_error')

    def _request(self, callback):
        self._festivityFactory.getProcessor().getTalismanToy(self._talismanID, lambda resultID, errorStr, ext: self._response(resultID, callback, ctx=ext, errStr=errorStr))


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


class ChangeTalismanBonusStageProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, nextStage):
        super(ChangeTalismanBonusStageProcessor, self).__init__()
        self.__nextStage = nextStage

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/changeTalismanBonusStage/server_error')

    def _request(self, callback):
        _logger.debug('Make server request to change talisman bonus stage: (nextStage - %s)', self.__nextStage)
        self._festivityFactory.getProcessor().changeTalismanBonusStage(self.__nextStage, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
