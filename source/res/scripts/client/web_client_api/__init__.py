# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/__init__.py
import json
import inspect
import logging
import weakref
from collections import namedtuple
from functools import partial
from itertools import chain
from new import instancemethod
from types import FunctionType, BooleanType, TypeType
from Event import Event
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
    __slots__ = ('required', 'type', 'default', 'deprecated', 'validator')

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

    def __validateField(cls, schema, key, data, required):
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

        objectClsBase = namedtuple('ObjectClsBase', data.keys())
        if cls.__methods:
            objectCls = type('ObjectCls', (objectClsBase,), {})
            obj = objectCls(**data)
            for key, value in cls.__methods.iteritems():
                setattr(obj, key, instancemethod(value, obj, objectCls))

        else:
            obj = objectClsBase(**data)
        return obj


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

    def decorator(cls):

        class _class(cls):
            w2c_name = name

            def __init__(self):
                for base in cls.__bases__:
                    base.__init__(self)

                super(_class, self).__init__()

            def getHandlers(self):
                if name and key:

                    class _meta(W2CSchemaMeta):

                        def __init__(cls, *args, **kwargs):
                            args[2][key] = Field(required=True, type=basestring)
                            super(_meta, cls).__init__(*args, **kwargs)

                    class _schema(W2CSchema):
                        __metaclass__ = _meta

                    subcommands = {wrapper.w2c_name:SubCommand(wrapper.w2c_schema, partial(wrapper, self)) for _, wrapper in inspect.getmembers(cls, inspect.ismethod) if getattr(wrapper, 'w2c_name', None)}
                    return [createSubCommandsHandler(self.w2c_name or cls.__name__.lower(), _schema, key, subcommands)]
                else:
                    return [ createCommandHandler(commandName=wrapper.w2c_name, commandSchema=wrapper.w2c_schema, handlerFunc=partial(wrapper, self), finiHandlerFunc=partial(getattr(cls, wrapper.w2c_fini), self) if wrapper.w2c_fini else None) for _, wrapper in inspect.getmembers(cls, inspect.ismethod) if getattr(wrapper, 'w2c_name', None) ]

        return _class

    return decorator


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

            def handler(self, cmd, ctx):
                _CallbackDispatcher(fn(self, cmd), ctx['callback'])

        else:

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
