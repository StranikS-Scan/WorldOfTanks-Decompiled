# Embedded file name: scripts/client/gui/shared/gui_items/processors/__init__.py
from collections import namedtuple
from debug_utils import *
from helpers import i18n
from adisp import process, async
from gui.SystemMessages import SM_TYPE
from gui.shared.utils import code2str
from gui.shared.gui_items.processors import plugins
ResultMsg = namedtuple('ResultMsg', 'success userMsg sysMsgType auxData')

def makeSuccess(userMsg = '', msgType = SM_TYPE.Information, auxData = None):
    return ResultMsg(True, userMsg, msgType, auxData)


def makeError(userMsg = '', msgType = SM_TYPE.Error, auxData = None):
    return ResultMsg(False, userMsg, msgType, auxData)


def makeI18nSuccess(sysMsgKey = '', auxData = None, *args, **kwargs):
    return makeSuccess(i18n.makeString(('#system_messages:%s' % sysMsgKey), *args, **kwargs), kwargs.get('type', SM_TYPE.Information), auxData)


def makeI18nError(sysMsgKey = '', auxData = None, *args, **kwargs):
    return makeError(i18n.makeString(('#system_messages:%s' % sysMsgKey), *args, **kwargs), kwargs.get('type', SM_TYPE.Error), auxData)


class Processor(object):
    """
    Request processor. Process server request, its response,
    given plugins and returns user string to show.
    """
    PLUGIN_RES_CODE = -33

    def __init__(self, plugins = list()):
        """
        Ctor.
        
        @param plugins: list of plugins
        """
        self.plugins = list()
        self.addPlugins(plugins)

    def getPluginsByType(self, pluginType):
        """
        Returns list of given type plugins.
        
        @param pluginType: ProcessorPlugin.TYPE.* value
        @return: list<Plugin>
        """
        return [ plugin for plugin in self.plugins if plugin.type == pluginType ]

    def addPlugin(self, plugin):
        """
        Adds new plugin to plugins list.
        
        @param plugin: <ProcessorPlugin> new plugin
        """
        raise plugin is not None or AssertionError('Invalid plugin')
        self.plugins.append(plugin)
        return

    def addPlugins(self, plugins):
        """
        Adds given @plugins list to the list.
        
        @param plugins: <list> plugins list
        """
        for plugin in plugins:
            self.addPlugin(plugin)

    def _errorHandler(self, code, errStr = '', ctx = None):
        """
        Error case handler. Will be called when server responses
        error code. Must return user-friendly error string.
        
        @param code: <int> server response code
        @return: <string> user-friendly error string
        """
        return makeError(errStr, auxData=ctx)

    def _successHandler(self, code, ctx = None):
        """
        Success case handler. Will be called when server responses
        success code. Must return user-friendly message string.
        
        @param code: <int> server response code
        @return: <string> user-friendly message string
        """
        return makeSuccess(auxData=ctx)

    def _response(self, code, callback, errStr = '', ctx = None):
        """
        Common server response handler. Call corresponded
        method for error or success cases.
        
        @param code: server response code
        @param callback: callback to be called
        """
        LOG_DEBUG('Server response', code, errStr, ctx)
        if code < 0:
            return callback(self._errorHandler(code, errStr=errStr, ctx=ctx))
        return callback(self._successHandler(code, ctx=ctx))

    @async
    @process
    def __validate(self, callback):
        """
        Validates all validate-plugins before server
        request to be sent.
        
        @param callback: callback to be called
        """
        yield lambda callback: callback(True)
        validators = self.getPluginsByType(plugins.ProcessorPlugin.TYPE.VALIDATOR)
        for plugin in validators:
            if not plugin.isEnabled:
                continue
            if plugin.isAsync:
                pres = yield plugin.validate()
            else:
                pres = plugin.validate()
            if not pres.success:
                LOG_WARNING('Request validation failed, processor: %s, validator: %s (%s)' % (self.__class__.__name__, plugin.__class__.__name__, str(plugin.__dict__)))
                callback(self._errorHandler(self.PLUGIN_RES_CODE, pres.errorMsg, pres.ctx))
                return

        callback(makeSuccess())

    @async
    @process
    def __confirm(self, callback):
        """
        Confirms all confirm-plugins before server
        request to be sent.
        
        @param callback: callback to be called
        """
        yield lambda callback: callback(True)
        confirmators = self.getPluginsByType(plugins.ProcessorPlugin.TYPE.CONFIRMATOR)
        for plugin in confirmators:
            if not plugin.isEnabled:
                continue
            if plugin.isAsync:
                pres = yield plugin.confirm()
            else:
                pres = plugin.confirm()
            if not pres.success:
                callback(makeError())
                return

        callback(makeSuccess())

    def _request(self, callback):
        """
        Server request function. Can be overridden
        by inherited classes.
        
        @param callback: function to be called after server response
        """
        callback(makeSuccess())

    @async
    @process
    def request(self, callback = None):
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
    """
    Items processor. Make operations with items like vehicle,
    tankman and etc.
    """

    def __init__(self, item, plugins = list()):
        """
        Ctor.
        
        @param item: item to process
        @param plugins: list of plugins
        """
        super(ItemProcessor, self).__init__(plugins)
        self.item = item

    def _response(self, code, callback, ctx = None, errStr = ''):
        """
        Common server response handler. Call corresponded
        method for error or success cases.
        
        @param code: server response code
        @param callback: callback to be called
        """
        if code < 0:
            LOG_ERROR("Server responses an error [%s] while process %s '%s'" % (code2str(code), self.item.itemTypeName, str(self.item)))
            return callback(self._errorHandler(code, ctx=ctx, errStr=errStr))
        return callback(self._successHandler(code, ctx=ctx))


class VehicleItemProcessor(ItemProcessor):
    """
    Vehicle component processor. Makes common vehicle and
    module validations before server request sending.
    """

    def __init__(self, vehicle, module, allowableTypes):
        """
        Ctor.
        
        @param vehicle: vehicle
        @param module: module to be installed
        @param allowableTypes: module allowable types
        """
        super(VehicleItemProcessor, self).__init__(module, [plugins.VehicleValidator(vehicle, False, prop={'isBroken': True,
          'isLocked': True}), plugins.ModuleValidator(module), plugins.ModuleTypeValidator(module, allowableTypes)])
        self.vehicle = vehicle
        self.allowableTypes = allowableTypes
