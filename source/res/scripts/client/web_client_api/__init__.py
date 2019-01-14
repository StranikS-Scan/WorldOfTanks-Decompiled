# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/__init__.py
import json
import inspect
import logging
import weakref
from functools import partial
from itertools import chain
from types import FunctionType, BooleanType, TypeType
from Event import Event
from helpers import uniprof
from soft_exception import SoftException
_logger = logging.getLogger(__name__)

class CommandHandler(object):

    def __init__(self, name=None, schema=None, handler=None, finiHandler=None):
        self.name = name
        self.schema = schema
        self.handler = handler
        self.finiHandler = finiHandler
        super(CommandHandler, self).__init__()

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class SubCommand(object):
    __slots__ = ('subSchema', 'handler')

    def __init__(self, subSchema=None, handler=None):
        self.handler = handler
        self.subSchema = subSchema
        super(SubCommand, self).__init__()

    def hasHandler(self):
        return self.handler is not None

    def hasSubSchema(self):
        return self.subSchema is not None


class ISchemeMeta(type):

    def validate(cls, data):
        raise NotImplementedError

    def setDefault(cls, data):
        raise NotImplementedError

    def toObject(cls, data):
        raise NotImplementedError


class Schema(object):
    __metaclass__ = ISchemeMeta

    @classmethod
    def instantiate(cls, data):
        cls.validate(data)
        finalData = cls.setDefault(data)
        return cls.toObject(finalData)


class Field(object):
    __slots__ = ('required', 'type', 'default', 'deprecated', 'validator', '__weakref__')

    def __init__(self, required=False, type=None, default=None, deprecated=None, validator=None):
        if required and default is not None:
            _logger.warning('Do not use "required" and "default" at the same time!')
        self.required = required
        self.type = type
        self.default = default
        self.deprecated = deprecated
        self.validator = validator
        super(Field, self).__init__()
        return

    def hasType(self):
        return self.type is not None

    def hasValidator(self):
        return self.validator is not None


class W2CSchemaMeta(ISchemeMeta):

    def __init__(cls, *args, **kwargs):
        super(W2CSchemaMeta, cls).__init__(*args, **kwargs)
        cls.__schema = {k:v for k, v in args[2].iteritems() if isinstance(v, Field)}
        cls.__methods = {k:v for k, v in args[2].iteritems() if isinstance(v, FunctionType)}

    def validate(cls, data):
        for key, value in cls.__schema.iteritems():
            error = cls.__validateField(value, key, data, value.required)
            if error:
                raise WebCommandException(error)

        if cls.__unions__:
            found = False
            for k in cls.__unions__:
                error = cls.__validateField(cls.__schema[k], k, data, True)
                if not error:
                    found = True

            if not found:
                raise WebCommandException('Command validation failed: Not found suitable parameters!')

    def setDefault(cls, data):
        for key, value in cls.__schema.iteritems():
            if key not in data:
                data[key] = value.default

        return data

    def toObject(cls, data):
        customParameters = set(data) - set(cls.__schema)
        data['custom_parameters'] = {}
        for name in customParameters:
            data['custom_parameters'][name] = data.pop(name)

        return Schema2Command(data, methods=cls.__methods)

    @staticmethod
    def __validateField(schema, key, data, required):
        if required and key not in data:
            return "Command validation failed: '%s' parameter is missing!" % key
        else:
            if key in data:
                if schema.hasType() and not isinstance(data[key], schema.type):
                    return "Command validation failed: Value '%s' for parameter '%s' is wrong!" % (data[key], key)
                if schema.hasValidator():
                    errmsg = ''
                    try:
                        isValid = schema.validator(data[key], data)
                    except SoftException as err:
                        isValid = False
                        errmsg = '; {}'.format(err)

                    if not isValid:
                        return 'Invalid value for field {}: {}{}'.format(key, data[key], errmsg)
                deprecatedMessage = schema.deprecated
                if deprecatedMessage is not None:
                    _logger.warning('"%s" parameter is deprecated (%s)!', key, deprecatedMessage)
            return


class Schema2Command(object):

    def __init__(self, data, methods=None):
        super(Schema2Command, self).__init__()
        self.__data = data
        self.__methods = methods.keys()
        for key, value in methods.iteritems():
            setattr(self, key, value.__get__(self))

    def clear(self):
        for name in self.__methods:
            delattr(self, name)

    def __getattr__(self, name):
        if name in self.__data:
            return self.__data[name]
        raise AttributeError('Property is not found in {0}: {1}'.format(self.__class__, name))


class W2CSchema(Schema):
    __metaclass__ = W2CSchemaMeta
    __unions__ = None


class WebCommandSchema(W2CSchema):
    command = Field(required=True, type=basestring)
    params = Field(required=True, type=dict)
    web_id = Field(type=basestring)


def instantiateCommand(schema, data):
    return schema.instantiate(data)


def createCommandHandler(commandName, commandSchema, handlerFunc, finiHandlerFunc=None):
    return CommandHandler(commandName, commandSchema, handlerFunc, finiHandlerFunc)


def createSubCommandsHandler(commandName, commandSchema, keyField, subCommands):

    def handlerFunc(command, ctx):
        key = getattr(command, keyField)
        if key in subCommands and subCommands[key].hasHandler():
            subCommand = subCommands[key]
            if subCommand.hasSubSchema():
                subCommandObj = instantiateCommand(subCommand.subSchema, command.custom_parameters)
                subCommand.handler(subCommandObj, ctx)
            else:
                subCommand.handler(command, ctx)
        else:
            raise WebCommandException("Unsupported value for '%s': '%s'" % (keyField, key))

    return createCommandHandler(commandName, commandSchema, handlerFunc)


def w2capi(name=None, key=None):
    return _W2CApi(name, key)


def _makeOverriddenMeta(key):

    def _get(*args, **kwargs):
        args[2][key] = Field(required=True, type=basestring)
        return W2CSchemaMeta(*args, **kwargs)

    return _get


def _makeOverriddenSchema(key):

    class _OverriddenSchema(W2CSchema):
        __metaclass__ = _makeOverriddenMeta(key)

    return _OverriddenSchema


class _W2CApi(object):

    def __init__(self, name, key):
        super(_W2CApi, self).__init__()
        self.__name = name
        self.__key = key

    def __call__(self, clazz):
        clazz.w2c_name = self.__name
        if self.__name and self.__key:

            def generate(key, scheme):

                def getter(api):
                    subcommands = {wrapper.w2c_name:SubCommand(wrapper.w2c_schema, partial(wrapper, api)) for _, wrapper in inspect.getmembers(clazz, inspect.ismethod) if getattr(wrapper, 'w2c_name', None)}
                    return [createSubCommandsHandler(api.w2c_name or clazz.__name__.lower(), scheme, key, subcommands)]

                return getter

            getHandlers = generate(self.__key, _makeOverriddenSchema(self.__key))
        else:

            def getHandlers(api):
                return [ createCommandHandler(commandName=wrapper.w2c_name, commandSchema=wrapper.w2c_schema, handlerFunc=partial(wrapper, api), finiHandlerFunc=partial(getattr(clazz, wrapper.w2c_fini), api) if wrapper.w2c_fini else None) for _, wrapper in inspect.getmembers(clazz, inspect.ismethod) if getattr(wrapper, 'w2c_name', None) ]

        clazz.getHandlers = getHandlers
        return clazz


class _CallbackDispatcher(object):

    def __init__(self, generator, handler):
        self.gen = generator
        self.handler = handler
        try:
            self.call(self.gen.next())
        except StopIteration:
            pass

    def call(self, callers):
        single = not inspect.isgenerator(callers)
        if single:
            callers = [callers]
        for caller in callers:
            if callable(caller):
                caller(callback=self.callback)
            self.handler(caller)

    def callback(self, arg):
        try:
            self.call(self.gen.send(arg))
        except StopIteration:
            pass


def w2c(schema, name='', finiHandlerName=None):

    def decorator(fn):
        if inspect.isgeneratorfunction(fn):

            @uniprof.regionDecorator(label='w2c {}'.format(name), scope='wrap')
            def handler(self, cmd, ctx):
                _CallbackDispatcher(fn(self, cmd), ctx['callback'])

        else:

            @uniprof.regionDecorator(label='w2c {}'.format(name), scope='wrap')
            def handler(self, cmd, ctx):
                argspec = inspect.getargspec(fn)
                return ctx['callback'](fn(self, cmd, ctx)) if 'ctx' in argspec.args and argspec.args.index('ctx') == 2 else ctx['callback'](fn(self, cmd))

        handler.w2c_schema = schema
        handler.w2c_name = name or fn.__name__
        handler.w2c_fini = finiHandlerName
        return handler

    return decorator


class WebCommandException(SoftException):
    pass


class WebCommandHandler(object):

    def __init__(self, browserID, alias, browserView):
        self.__handlers = {}
        self.__browserID = browserID
        self.__alias = alias
        self.__browserView = weakref.proxy(browserView)
        self.onCallback = Event()

    def fini(self):
        for handler in self.__handlers.itervalues():
            finiHandler = handler.finiHandler
            if callable(finiHandler):
                finiHandler()

        self.__handlers = {}

    def handleCommand(self, data):
        _logger.debug('Web2Client handle: %s', data)
        try:
            parsed = json.loads(data, encoding='utf-8')
        except (TypeError, ValueError) as exception:
            raise WebCommandException('Command parse failed! Description: %s' % exception)

        command = instantiateCommand(WebCommandSchema, parsed)
        self.handleWebCommand(command)
        command.clear()

    def addHandlers(self, handlers):
        for handler in handlers:
            self.addHandler(handler)

    def addHandler(self, handler):
        if handler.name not in self.__handlers:
            self.__handlers[handler.name] = handler
        else:
            raise WebCommandException('Handler for command `%s` is already registered!' % handler.name)

    def removeHandler(self, handler):
        self.__handlers.pop(handler.name, None)
        return

    def handleWebCommand(self, webCommand):
        commandName = webCommand.command
        handler = self.__handlers.get(commandName)
        if handler is None:
            raise WebCommandException("Command '%s' is unsupported!" % commandName)
        command = instantiateCommand(handler.schema, webCommand.params)
        handler.handler(command, self.__createCtx(commandName, webCommand.web_id))
        command.clear()
        return

    def __createCtx(self, commandName, webId):

        def callback(data):
            callbackData = {'command': commandName,
             'data': data,
             'web_id': webId}
            _logger.debug('Web2Client callback: %s', callbackData)
            jsonMessage = json.dumps(callbackData)
            self.onCallback(jsonMessage)

        return {'browser_id': self.__browserID,
         'browser_alias': self.__alias,
         'browser_view': self.__browserView,
         'callback': callback}


def webApiCollection(*apiProviders):
    return list(chain.from_iterable((provider().getHandlers() for provider in apiProviders)))
