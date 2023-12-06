# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/__init__.py
import logging
import typing
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from helpers import dependency
from helpers import i18n
from adisp import adisp_process, adisp_async
from gui.SystemMessages import SM_TYPE, ResultMsg
from gui.shared.money import Currency
from gui.shared.utils import code2str
from gui.shared.gui_items.processors import plugins as proc_plugs
from skeletons.gui.shared import IItemsCache
from collections import namedtuple
_logger = logging.getLogger(__name__)

def makeSuccess(userMsg='', msgType=SM_TYPE.Information, auxData=None, msgData=None, msgPriority=None):
    return ResultMsg(True, userMsg, msgType, msgPriority, msgData if msgData is not None else {}, auxData)


def makeError(userMsg='', msgType=SM_TYPE.Error, auxData=None, msgData=None, msgPriority=None):
    return ResultMsg(False, userMsg, msgType, msgPriority, msgData if msgData is not None else {}, auxData)


def makeI18nSuccess(sysMsgKey='', auxData=None, *args, **kwargs):
    return makeSuccess(i18n.makeString('#system_messages:{}'.format(sysMsgKey), *args, **kwargs), kwargs.get('type', SM_TYPE.Information), auxData)


def makeI18nError(sysMsgKey='', defaultSysMsgKey='', auxData=None, *args, **kwargs):
    localKey = '#system_messages:{}'.format(sysMsgKey)
    if localKey not in SYSTEM_MESSAGES.ALL_ENUM and defaultSysMsgKey:
        localKey = '#system_messages:{}'.format(defaultSysMsgKey)
    return makeError(i18n.makeString(localKey, *args, **kwargs), kwargs.get('type', SM_TYPE.Error), auxData)


def makeNYSuccess(sysMsgKey='', msgType=SM_TYPE.Information, auxData=None, *args, **kwargs):
    return makeSuccess(i18n.makeString('#ny:{}'.format(sysMsgKey), *args, **kwargs), msgType, auxData)


def makeCrewSkinCompensationMessage(comp):
    compMsg = None
    if comp is not None:
        amount = comp.price.get(Currency.CREDITS, None)
        if amount is not None:
            compMsg = makeI18nSuccess(sysMsgKey='crewSkinsCompensation/success', compensation=amount, type=SM_TYPE.SkinCompensation)
    return compMsg


class GroupedServerResponse(namedtuple('GroupedServerResponse', ['itemID', 'itemCount'])):

    def __new__(cls, *args, **kwargs):
        data = dict(itemID=-1, itemCount=0)
        data.update(dict(((field, val) for field, val in zip(cls._fields[:len(args)], args))))
        data.update(kwargs)
        return super(GroupedServerResponse, cls).__new__(cls, **data)


class Processor(object):
    itemsCache = dependency.descriptor(IItemsCache)
    PLUGIN_RES_CODE = -33

    def __init__(self, plugins=None):
        self.plugins = []
        self.addPlugins(plugins or [])
        self.requestCtx = {}
        self.responseCtx = {}

    def getPluginsByType(self, pluginType):
        return [ plugin for plugin in self.plugins if plugin.type == pluginType ]

    def addPlugin(self, plugin):
        if plugin is not None:
            self.plugins.append(plugin)
        else:
            _logger.error('Instance of plugin is None')
        return

    def addPlugins(self, plugins):
        for plugin in plugins:
            self.addPlugin(plugin)

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeError(errStr, auxData=ctx)

    def _successHandler(self, code, ctx=None):
        return makeSuccess(auxData=ctx)

    def _response(self, code, callback, errStr='', ctx=None):
        if code >= 0:
            _logger.debug('Server success response: code=%r, error=%r, ctx=%r', code, errStr, ctx)
            return callback(self._successHandler(code, ctx=ctx))
        _logger.warning('Server fail response: code=%r, error=%r, ctx=%r', code, errStr, ctx)
        return callback(self._errorHandler(code, errStr=errStr, ctx=ctx))

    @adisp_async
    @adisp_process
    def __validate(self, callback):
        yield lambda callback: callback(True)
        validators = self.getPluginsByType(proc_plugs.ProcessorPlugin.TYPE.VALIDATOR)
        for plugin in validators:
            if not plugin.isEnabled:
                continue
            if plugin.isAsync:
                pres = yield plugin.validate()
            else:
                pres = plugin.validate()
            if not pres.success:
                callback(self._errorHandler(self.PLUGIN_RES_CODE, pres.errorMsg, pres.ctx))
                if pres.errorMsg not in self._skippedWarnings():
                    _logger.warning('Request validation failed, processor: %s, validator: %s (%s)', self.__class__.__name__, plugin.__class__.__name__, str(plugin.__dict__))
                return

        callback(makeSuccess())

    def _skippedWarnings(self):
        return []

    @adisp_async
    @adisp_process
    def __confirm(self, callback):
        yield lambda callback: callback(True)
        confirmators = self.getPluginsByType(proc_plugs.ProcessorPlugin.TYPE.CONFIRMATOR)
        for plugin in confirmators:
            if not plugin.isEnabled:
                continue
            if plugin.isAsync:
                pres = yield plugin.confirm()
            else:
                pres = plugin.confirm()
            self.responseCtx.update(pres.ctx)
            if not pres.success:
                callback(makeError())
                return
            self.requestCtx.update(pres.ctx)

        callback(makeSuccess())

    def _request(self, callback):
        callback(makeSuccess())

    @adisp_async
    @adisp_process
    def request(self, callback=None):
        res = yield self.__confirm()
        if not res.success:
            callback(res)
            return
        res = yield self.__validate()
        if not res.success:
            callback(res)
            return
        self._request(callback)


class ItemProcessor(Processor):

    def __init__(self, item, plugins=None):
        super(ItemProcessor, self).__init__(plugins or [])
        self.item = item

    def _response(self, code, callback, ctx=None, errStr=''):
        if code < 0:
            _logger.error("Server responses an error [%s] while process %s '%s'", code2str(code), self.item.itemTypeName, str(self.item))
            return callback(self._errorHandler(code, ctx=ctx, errStr=errStr))
        return callback(self._successHandler(code, ctx=ctx))


class GroupedRequestProcessor(Processor):

    def __init__(self, request, *args, **kwargs):
        super(GroupedRequestProcessor, self).__init__(plugins=kwargs.get('plugins'))
        self.__request = request
        self.__params = args
        self.__groupID = kwargs.get('groupID', 0)
        self.__groupSize = kwargs.get('groupSize', 1)

    def _request(self, callback):
        _logger.debug('Make server request {}: '.format(self.__request.__name__) + ', '.join((str(i) for i in self.__params)))
        self.__request(*(self.__params + (self.__groupID, self.__groupSize, lambda code, errStr, ctx=None: self._response(code, callback, errStr=errStr, ctx=ctx))))
        return

    def _response(self, code, callback, ctx=None, errStr=''):
        items = list((GroupedServerResponse(*itemConfig) for itemConfig in ctx)) if ctx else []
        if code < 0:
            _logger.warning('Server fail response: code=%r, error=%r, ctx=%r', code, errStr, ctx)
            return callback(self._errorHandler(code, errStr=errStr, ctx=items) if ctx else makeError())
        _logger.debug('Server success response: code=%r, ctx=%r', code, ctx)
        return callback(self._successHandler(code, ctx=items) if ctx else makeSuccess())

    def _makeSuccessData(self, *args, **kwargs):
        return [makeSuccess()]

    def _makeErrorData(self, *args, **kwargs):
        return [makeError()]


class VehicleItemProcessor(ItemProcessor):

    def __init__(self, vehicle, module, allowableTypes):
        super(VehicleItemProcessor, self).__init__(module, [proc_plugs.VehicleValidator(vehicle, False, prop={'isBroken': True,
          'isLocked': True}), proc_plugs.ModuleValidator(module), proc_plugs.ModuleTypeValidator(module, allowableTypes)])
        self.vehicle = vehicle
        self.allowableTypes = allowableTypes
