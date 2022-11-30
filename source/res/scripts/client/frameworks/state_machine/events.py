# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/state_machine/events.py


class StateEvent(object):
    __slots__ = ('__arguments',)

    def __init__(self, *args, **kwargs):
        super(StateEvent, self).__init__()
        self.__arguments = kwargs

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, id(self))

    def getArgument(self, name, default=None):
        return self.__arguments.get(name, default)

    def getArguments(self):
        return self.__arguments


class StringEvent(StateEvent):
    __slots__ = ('__token',)

    def __init__(self, token, **kwargs):
        super(StringEvent, self).__init__(**kwargs)
        self.__token = token

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.__token)

    @property
    def token(self):
        return self.__token
