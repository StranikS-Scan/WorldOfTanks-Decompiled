# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/command.py
from types import FunctionType, BooleanType, TypeType
from new import instancemethod
from collections import namedtuple
from debug_utils import LOG_WARNING
from .. import WebCommandException

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
            LOG_WARNING('Do not use "required" and "default" at the same time!')
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
                    error = schema.validator(data[key], data)
                    if error:
                        return error
                deprecatedMessage = schema.deprecated
                if deprecatedMessage is not None:
                    LOG_WARNING('"%s" parameter is deprecated (%s)!' % (key, deprecatedMessage))
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


def createCommandHandler(commandName, commandSchema, handlerFunc, finiFunc=None):
    return CommandHandler(commandName, commandSchema, handlerFunc, finiFunc)


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
