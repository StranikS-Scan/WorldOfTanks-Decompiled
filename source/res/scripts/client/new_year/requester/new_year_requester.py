# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/requester/new_year_requester.py
import BigWorld
from AccountCommands import RES_FAILURE
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.locale.NY import NY
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.requesters.RequestsController import RequestsController
from gui.shared.utils.requesters.abstract import ClientRequestsByIDProcessor
from helpers import i18n, dependency
from items.new_year_types import NY_STATE, TOY_TYPES_IDS_BY_NAME, NATIONAL_SETTINGS_IDS_BY_NAME, MAX_TOY_RANK, INVALID_TOY_ID
from shared_utils import CONST_CONTAINER
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_SERVER_REQUEST_TIME_OUT = 30.0

class ResponseCodes(CONST_CONTAINER):
    CLIENT_CTRL_ERROR = -555
    CLIENT_VALIDATOR_ERROR = -556


class RequestType(CONST_CONTAINER):
    OPEN_BOX = 1
    OPEN_CHEST = 2
    APPLY_VEH_DISCOUNT = 3
    RECRUIT_TANK_WOMAN = 4
    CRAFT_TOY = 5
    BREAK_TOYS = 6
    PLACE_TOY = 7


class _NYRequester(ClientRequestsByIDProcessor):

    def __init__(self):
        super(_NYRequester, self).__init__(BigWorld.player().newYear)

    def makeInternalSuccessResponse(self, txtMsg='', data=None, ctx=None):
        return self._makeResponse(0, txtMsg, data, ctx)

    def makeInternalErrorResponse(self, code, txtMsg, ctx):
        return self._makeResponse(code, txtMsg, None, ctx)

    def _doCall(self, method, *args, **kwargs):
        requestID = self._idsGenerator.next()

        def _callback(requestId, code, txtMsg, ext):
            ctx = self._requests.get(requestID)
            self._onResponseReceived(requestID, self._makeResponse(code, txtMsg, ext, ctx))

        method(callback=_callback, *args, **kwargs)
        return requestID


class NYRequestController(RequestsController):
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, nyCtrl):
        super(NYRequestController, self).__init__(_NYRequester())
        self._nyCtrl = nyCtrl
        self.__handlersEnv = {RequestType.OPEN_BOX: (self.__openBox, self.__validateBoxesData, self.__containerResponseHandler),
         RequestType.OPEN_CHEST: (self.__openChest, self.__validateChestsData, self.__containerResponseHandler),
         RequestType.RECRUIT_TANK_WOMAN: (self.__recruitTankmen, self.__validateTankmen, self.__recruitResponseHandler),
         RequestType.APPLY_VEH_DISCOUNT: (self.__applyVehDiscount, self.__validateVehDiscount, self.__vehDiscountResponseHandler),
         RequestType.CRAFT_TOY: (self.__craftToy, self.__validateCraftParams, self.__craftResponseHandler),
         RequestType.BREAK_TOYS: (self.__breakToys, self.__validateBreakingToysParams, self.__breakToysResponseHandler),
         RequestType.PLACE_TOY: (self.__placeToy, self.__validatePlacingToyParams, self.__placeToyResponseHandler)}

    def fini(self):
        super(NYRequestController, self).fini()
        self.__handlersEnv.clear()
        self._nyCtrl = None
        return

    def validateRequest(self, ctx, callback=lambda *args: None):
        """
        Check all requirements before request sending
        :param ctx: ny_contexts._CommonNYContext
        :param callback: function that will be invoked
        :return: True if all data is valid and request could be sent
        """

        def __handle_error(code, txt, sysMsg):
            if sysMsg:
                SystemMessages.pushI18nMessage(sysMsg, type=SystemMessages.SM_TYPE.Error)
            callback(self._requester.makeInternalErrorResponse(code, txt, ctx))

        if self._nyCtrl.state == NY_STATE.NOT_STARTED or self._nyCtrl.state == NY_STATE.SUSPENDED:
            __handle_error(ResponseCodes.CLIENT_CTRL_ERROR, 'NY Controller is unavailable', NY.SYSTEM_MESSAGES_REQUEST_ERROR_COMMON)
            return False
        isValid, sysMsg = self.__handlersEnv[ctx.getRequestType()][1](ctx)
        if not isValid:
            __handle_error(ResponseCodes.CLIENT_VALIDATOR_ERROR, 'NY Validation has not been passed', sysMsg)
            return False
        if not ctx.multipleRequestAllowed():
            if self.isProcessing(ctx.getWaiterID()):
                __handle_error(ResponseCodes.CLIENT_CTRL_ERROR, 'Request is being process', NY.SYSTEM_MESSAGES_REQUEST_ERROR_REQUESTISBEINGPROCESS)
                return False
        return True

    def request(self, ctx, callback=lambda *args: None, allowDelay=None):

        def _cbWrapper(response):
            self.__handlersEnv[ctx.getRequestType()][2](response, ctx)
            callback(response)

        if self.validateRequest(ctx, callback):
            super(NYRequestController, self).request(ctx, _cbWrapper, allowDelay)
            return True
        return False

    def _getRequestTimeOut(self):
        return _SERVER_REQUEST_TIME_OUT

    def _getHandlerByRequestType(self, requestTypeID):
        return self.__handlersEnv[requestTypeID][0]

    def __openBox(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, 'openBox', ctx.getID())

    def __openChest(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, 'openChest', ctx.getID())

    def __applyVehDiscount(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, 'selectDiscount', ctx.getDiscountID(), ctx.getVariadicDiscountID())

    def __recruitTankmen(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, 'selectTankman', ctx.getNationID(), ctx.getVehicleInnationID(), ctx.getRoleID(), ctx.getVariadicTankmanID())

    def __craftToy(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, 'craft', ctx.getToyType(), ctx.getToyNation(), ctx.getToyLevel())

    def __breakToys(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, 'breakToys', ctx.getToys())

    def __placeToy(self, ctx, callback):
        return self._requester.doRequestEx(ctx, callback, 'fillSlot', ctx.getSlotID(), ctx.getToyID())

    def __validateBoxesData(self, ctx):
        if self._nyCtrl.state == NY_STATE.FINISHED:
            return (False, NY.SYSTEM_MESSAGES_REQUEST_ERROR_COMMON)
        box_id = ctx.getID()
        filterFunc = lambda q: q.getID() == box_id
        quests = self._eventsCache.getHiddenQuests(filterFunc=filterFunc)
        if not quests:
            return (False, NY.SYSTEM_MESSAGES_REQUEST_ERROR_COMMON)
        return (False, NY.SYSTEM_MESSAGES_OPEN_ERROR_NO_ITEMS) if box_id not in self._nyCtrl.boxStorage.getDescriptors() else (True, '')

    def __validateChestsData(self, ctx):
        if self._nyCtrl.state == NY_STATE.FINISHED:
            return (False, NY.SYSTEM_MESSAGES_REQUEST_ERROR_COMMON)
        chest_id = ctx.getID()
        filterFunc = lambda q: q.getID() == chest_id
        quests = self._eventsCache.getHiddenQuests(filterFunc=filterFunc)
        if not quests:
            return (False, NY.SYSTEM_MESSAGES_REQUEST_ERROR_COMMON)
        return (False, NY.SYSTEM_MESSAGES_OPEN_ERROR_NO_ITEMS) if chest_id not in self._nyCtrl.chestStorage.getDescriptors() else (True, '')

    def __validateVehDiscount(self, ctx):
        discounts = self._nyCtrl.vehDiscountsStorage.getDiscounts()
        if self._itemsCache.items.getItemByCD(typeCompDescr=ctx.getVehIntCD()).isInInventory:
            return (False, NY.SYSTEM_MESSAGES_DISCOUNTSELECT_ERROR_INHANGAR)
        elif not discounts or not sum(discounts.values()):
            return (False, NY.SYSTEM_MESSAGES_DISCOUNTSELECT_ERROR_NO_DISCOUNTS)
        elif discounts.get(ctx.getVariadicDiscountID(), 0):
            return (True, '')
        else:
            return (False, NY.SYSTEM_MESSAGES_DISCOUNTSELECT_ERROR_NOT_FOUND)

    def __validateTankmen(self, ctx):
        discounts = self._nyCtrl.tankmanDiscountsStorage.getDiscounts()
        if not discounts or not sum(discounts.values()):
            return (False, NY.SYSTEM_MESSAGES_TANKMANRECRUIT_ERROR_NO_DISCOUNTS)
        elif discounts.get(ctx.getVariadicTankmanID(), 0):
            return (True, '')
        else:
            return (False, NY.SYSTEM_MESSAGES_TANKMANRECRUIT_ERROR_NOT_FOUND)

    def __validateCraftParams(self, ctx):
        if self._nyCtrl.state == NY_STATE.FINISHED:
            return (False, NY.SYSTEM_MESSAGES_REQUEST_ERROR_COMMON)
        else:
            toyType = ctx.getToyType()
            if toyType is not None:
                if TOY_TYPES_IDS_BY_NAME.get(toyType) is None:
                    return (False, NY.SYSTEM_MESSAGES_CRAFTTOY_ERROR_INVALIDREQUEST)
            nationalSetting = ctx.getToyNation()
            if nationalSetting is not None:
                if NATIONAL_SETTINGS_IDS_BY_NAME.get(nationalSetting) is None:
                    return (False, NY.SYSTEM_MESSAGES_CRAFTTOY_ERROR_INVALIDREQUEST)
            rank = ctx.getToyLevel()
            if rank is not None and (rank > MAX_TOY_RANK or rank < 0):
                return (False, NY.SYSTEM_MESSAGES_CRAFTTOY_ERROR_INVALIDREQUEST)
            return (True, '')

    def __validateBreakingToysParams(self, ctx):
        if self._nyCtrl.state == NY_STATE.FINISHED:
            return (False, NY.SYSTEM_MESSAGES_REQUEST_ERROR_COMMON)
        toys = ctx.getToys()
        if toys:
            toysIdToCountDict = dict(((k, v.totalCount) for k, v in self._nyCtrl.toysDataDict.iteritems()))
            for slot in self._nyCtrl.slots:
                if slot.id > 0:
                    if slot.id in toysIdToCountDict:
                        toysIdToCountDict[slot.id] += 1
                    else:
                        toysIdToCountDict[slot.id] = 1

            for toyId, _ in toys:
                if toysIdToCountDict.get(toyId, 0) <= 0:
                    return (False, NY.SYSTEM_MESSAGES_BREAKTOYS_ERROR_INVALIDREQUEST)
                toysIdToCountDict[toyId] -= 1

        else:
            return (False, NY.SYSTEM_MESSAGES_BREAKTOYS_ERROR_INVALIDREQUEST)
        return (True, '')

    def __validatePlacingToyParams(self, ctx):
        if self._nyCtrl.state == NY_STATE.FINISHED:
            return (False, NY.SYSTEM_MESSAGES_REQUEST_ERROR_COMMON)
        else:
            toyID = ctx.getToyID()
            slotID = ctx.getSlotID()
            slotDescrs = self._nyCtrl.slotsDescrs
            slotType = slotDescrs[slotID].type if 0 <= slotID <= len(slotDescrs) else None
            if slotType is None:
                return (False, NY.SYSTEM_MESSAGES_PLACETOY_ERROR_INVALIDREQUEST)
            if toyID != INVALID_TOY_ID:
                if toyID not in self._nyCtrl.getInventory()[slotType]:
                    return (False, NY.SYSTEM_MESSAGES_PLACETOY_ERROR_INVALIDREQUEST)
            descrs = self._nyCtrl.getPlacedToys((slotID,))
            placedToyDescr = descrs.get(slotID)
            if placedToyDescr:
                if placedToyDescr.id == toyID:
                    LOG_DEBUG('[NEW YEAR] Toy with id = {} has been installed in slot {} already'.format(toyID, slotID))
                    return (False, '')
            return (True, '')

    def __containerResponseHandler(self, response, ctx):
        if self.__commonResponseHandler(response, ctx):
            return
        if not response.isSuccess():
            SystemMessages.pushI18nMessage(NY.SYSTEM_MESSAGES_OPEN_ERROR_SERVER_ERROR, type=SystemMessages.SM_TYPE.Error)

    def __vehDiscountResponseHandler(self, response, ctx):
        if self.__commonResponseHandler(response, ctx):
            return
        if response.isSuccess():
            SystemMessages.pushI18nMessage(i18n.makeString(NY.SYSTEM_MESSAGES_DISCOUNTSELECT_SUCCESS, vehicle=ctx.getVehName(), discount=ctx.getDiscountVal()), type=SystemMessages.SM_TYPE.Information, priority=NotificationPriorityLevel.HIGH)
        else:
            SystemMessages.pushI18nMessage(NY.SYSTEM_MESSAGES_DISCOUNTSELECT_ERROR_SERVER_ERROR, type=SystemMessages.SM_TYPE.Error)

    def __recruitResponseHandler(self, response, ctx):
        if self.__commonResponseHandler(response, ctx):
            return
        if not response.isSuccess():
            SystemMessages.pushI18nMessage(NY.SYSTEM_MESSAGES_TANKMANRECRUIT_ERROR_SERVER_ERROR, type=SystemMessages.SM_TYPE.Error)

    def __commonResponseHandler(self, response, ctx):
        """
        Processes common errors.
        :param response: gui.shared.utils.requesters.abstract.Response
        :param ctx: new_year.requester.ny_contexts.CommonNYContext
        :return: True if error has been successfully processed, otherwise False
        """
        if not response.isSuccess():
            if response.getCode() == RES_FAILURE:
                errMsg = NY.system_messages_request_error(response.getTxtString())
                if errMsg:
                    SystemMessages.pushI18nMessage(errMsg, type=SystemMessages.SM_TYPE.Error)
                    return True
        else:
            return False

    def __craftResponseHandler(self, response, ctx):
        if self.__commonResponseHandler(response, ctx):
            return
        if not response.isSuccess():
            SystemMessages.pushI18nMessage(NY.SYSTEM_MESSAGES_CRAFTTOY_ERROR_SERVER_ERROR, type=SystemMessages.SM_TYPE.Error)

    def __breakToysResponseHandler(self, response, ctx):
        if self.__commonResponseHandler(response, ctx):
            return
        if not response.isSuccess():
            SystemMessages.pushI18nMessage(NY.SYSTEM_MESSAGES_BREAKTOYS_ERROR_SERVER_ERROR, type=SystemMessages.SM_TYPE.Error)

    def __placeToyResponseHandler(self, response, ctx):
        if self.__commonResponseHandler(response, ctx):
            return
        if not response.isSuccess():
            SystemMessages.pushI18nMessage(NY.SYSTEM_MESSAGES_PLACETOY_ERROR_SERVER_ERROR, type=SystemMessages.SM_TYPE.Error)
