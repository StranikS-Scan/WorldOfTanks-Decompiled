# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_processor.py
import logging
from pprint import pformat
import AccountCommands
from items import ny19
from items.components.ny_constants import TOY_DECAY_COST_BY_RANK
from helpers import dependency
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles, icons
from gui.shared.gui_items.processors import Processor, makeI18nError, plugins
from skeletons.festivity_factory import IFestivityFactory
_logger = logging.getLogger()

def _defaultLogger(*args):
    msg = pformat(args)
    _logger.debug('[SERVER CMD RESPONSE]:%s', msg)


def _getProxy(callback):
    return (lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr, ext)) if callback is not None else None


class NewYearCommandsProcessor(object):

    def __init__(self):
        super(NewYearCommandsProcessor, self).__init__()
        self.__commandProxy = None
        return

    def setCommandProxy(self, account):
        self.__commandProxy = account

    def hangToy(self, toyID, slotID, callback=None):
        self.__commandProxy.perform(AccountCommands.CMD_NEW_YEAR_SLOT_FILL, slotID, toyID, 0, _getProxy(callback))

    def applyVariadicDiscount(self, goodiesID, discountID, callback=None):
        self.__commandProxy.perform(AccountCommands.CMD_NEW_YEAR_SELECT_DISCOUNT, goodiesID, discountID, _getProxy(callback))

    def craftToy(self, toyTypeID, settingID, rank, callback=None):
        self.__commandProxy.perform(AccountCommands.CMD_NEW_YEAR_CRAFT, toyTypeID, settingID, rank, _getProxy(callback))

    def breakToys(self, toys, callback=None):
        self.__commandProxy.perform(AccountCommands.CMD_NEW_YEAR_BREAK_TOYS, toys, _getProxy(callback))

    def sendSeen(self, seenToys):
        self.__commandProxy.perform(AccountCommands.CMD_NEW_YEAR_SEE_INVENTORY_TOYS, seenToys, _defaultLogger)

    def seenInCollection(self, seenToys):
        self.__commandProxy.perform(AccountCommands.CMD_NEW_YEAR_SEE_COLLECTION_TOYS, seenToys, _defaultLogger)

    def viewAlbum(self, settingID, rank):
        self.__commandProxy.perform(AccountCommands.CMD_NEW_YEAR_VIEW_ALBUM, settingID, rank, 0, _defaultLogger)

    def buyToy(self, toyID, callback=None):
        self.__commandProxy.perform(AccountCommands.CMD_NEW_YEAR_CRAFT_OLD_TOYS, toyID, 0, 0, _getProxy(callback))

    def addToys(self, toysDict=None):
        if toysDict:
            toysToAdd = []
            for toyID, count in toysDict.iteritems():
                toysToAdd.extend([toyID] * count)

        else:
            toysToAdd = ny19.g_cache.toys.keys()
        self.__commandProxy.perform(AccountCommands.CMD_NEW_YEAR_ADD_TOYS_DEV, toysToAdd, _defaultLogger)


class CraftProcessor(Processor):
    _festivityFactory = dependency.descriptor(IFestivityFactory)

    def __init__(self, toyTypeID, settingID, rank):
        super(CraftProcessor, self).__init__()
        self.__toyTypeID = toyTypeID
        self.__settingID = settingID
        self.__rankID = rank

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/craftToy/server_error')

    def _request(self, callback):
        _logger.debug('Make server request to craft toyTypeID: %s, settingID: %s, rank: %s', self.__toyTypeID, self.__settingID, self.__rankID)
        self._festivityFactory.getProcessor().craftToy(self.__toyTypeID, self.__settingID, self.__rankID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))


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

    def __init__(self, toysToBreak, expectedShardsCount):
        threshold = max(TOY_DECAY_COST_BY_RANK.values())
        confirmator = [self.__buildConfirmator(expectedShardsCount)] if expectedShardsCount >= threshold else None
        super(NewYearBreakToysProcessor, self).__init__(confirmator)
        self.__toysToBreak = self.__prepareToysServerFormat(toysToBreak)
        return

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/breakToys/server_error')

    def _request(self, callback):
        self._festivityFactory.getProcessor().breakToys(self.__toysToBreak, lambda resultID, errorStr, ext: self._response(resultID, callback, ctx=ext, errStr=errorStr))

    @staticmethod
    def __buildConfirmator(expectedShardsCount):
        messageCtx = {'price': '{}{}'.format(icons.makeImageTag(RES_ICONS.MAPS_ICONS_NEW_YEAR_ICONS_PARTS_24X24, width=24, height=24, vSpace=-8), text_styles.credits(expectedShardsCount))}
        return plugins.MessageConfirmator('breakDecorations', ctx=messageCtx)

    @staticmethod
    def __prepareToysServerFormat(toysToBreak):
        toysToBreakServerFormat = []
        for k, v in toysToBreak.iteritems():
            toysToBreakServerFormat.append(k)
            toysToBreakServerFormat.append(v)

        return toysToBreakServerFormat


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

    def __init__(self, toyID, price):
        messageCtx = {'price': '{}{}'.format(text_styles.credits(price), icons.makeImageTag(RES_ICONS.MAPS_ICONS_NEW_YEAR_ICONS_PARTS_24X24, width=24, height=24, vSpace=-8))}
        confirmator = plugins.MessageConfirmator('newYear/buyToy', ctx=messageCtx)
        super(BuyToyProcessor, self).__init__([confirmator])
        self.__toyID = int(toyID)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('newYear/buyToy/server_error')

    def _request(self, callback):
        _logger.debug('Make server request to buy toy toyD: %s', self.__toyID)
        self._festivityFactory.getProcessor().buyToy(self.__toyID, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))
