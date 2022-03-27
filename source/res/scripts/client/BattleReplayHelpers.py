# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BattleReplayHelpers.py
import functools
import inspect
import itertools
import logging
import weakref
import BattleReplay
from shared_utils import unwrap
from skeletons.battle_replay import IReplayConvertible
_logger = logging.getLogger(__name__)

def _getClassName(method):
    for depth in xrange(len(inspect.stack())):
        code = inspect.currentframe(depth).f_code
        if '__init__' in code.co_names and method.__name__ in code.co_names:
            return code.co_name


def _getArgsStr(method):
    spec = inspect.getargspec(method)
    return '({})'.format(', '.join(itertools.chain(spec.args, ('*{}'.format(spec.varargs),) if spec.varargs is not None else (), ('**{}'.format(spec.keywords),) if spec.keywords is not None else ())))


def _makeMethodUniqueName(method):
    method = unwrap(method)
    return '{}{}'.format('.'.join((inspect.getmodule(method).__name__, _getClassName(method), method.__name__)), _getArgsStr(method))


def _makeConverters(argsNames, argsConverters, kwargsConverters):
    return tuple(((argNdx, argName, converter) for argNdx, argName, converter in itertools.chain(((argNdx, argName, converter or kwargsConverters.get(argName)) for argNdx, (argName, converter) in enumerate(itertools.izip_longest(argsNames, argsConverters)) if converter or kwargsConverters.get(argName)), ((None, kwargName, converter) for kwargName, converter in kwargsConverters.iteritems() if kwargName not in argsNames)) if issubclass(converter, IReplayConvertible)))


def _convertTypes(direction, converters, argsValues, kwargsValues):
    if not converters:
        return (argsValues, kwargsValues)
    else:
        newArgs, newKwargs = list(argsValues), dict(kwargsValues)
        for aNdx, aName, converter in converters:
            if aNdx is not None and len(newArgs) > aNdx:
                newArgs[aNdx] = getattr(converter, direction)(newArgs[aNdx])
            if aName in newKwargs:
                newKwargs[aName] = getattr(converter, direction)(newKwargs[aName])

        return (tuple(newArgs), newKwargs)


def _optionalArgsDecorator(decorator):

    @functools.wraps(decorator)
    def wrappedDecorator(*args, **kwargs):
        if not kwargs and len(args) == 1 and callable(args[0]):
            return decorator(args[0])

        def realDecorator(decoratee):
            return decorator(decoratee, *args, **kwargs)

        return realDecorator

    return wrappedDecorator


@_optionalArgsDecorator
def replayMethod(method=None, *argsTypes, **kwargsTypes):
    callbackName = str(hash(_makeMethodUniqueName(method)))

    @functools.wraps(method)
    def wrapped(self, *args, **kwargs):
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.serializeCallbackData(callbackName, _convertTypes(IReplayConvertible.dumpSafe.__name__, wrapped.converters, args, kwargs))
        return method(self, *args, **kwargs)

    wrapped.method = method
    wrapped.callbackName = callbackName
    wrapped.converters = _makeConverters(inspect.getargspec(method).args[1:], argsTypes, kwargsTypes)
    return wrapped


def replayPlayer(cls):
    _realInit = cls.__init__

    def _init(self, *args, **kwargs):
        if BattleReplay.g_replayCtrl.isPlaying:
            self.__replayCallbacks = {wrapped.callbackName:functools.partial(self.__replayPlayMethod, wrapped) for wrapped in (member.__func__ for _, member in inspect.getmembers(self, inspect.ismethod)) if getattr(wrapped, 'callbackName', None) is not None}
            BattleReplay.g_replayCtrl.registerPlayer(self)
        _realInit(self, *args, **kwargs)

    def _iterReplayCallbacks(self):
        return self.__replayCallbacks.iteritems()

    def _replayPlayMethod(self, wrapped, args, kwargs):
        args, kwargs = _convertTypes(IReplayConvertible.loadSafe.__name__, wrapped.converters, args, kwargs)
        wrapped.method(self, *args, **kwargs)

    setattr(cls, '__init__', _init)
    setattr(cls, 'iterReplayCallbacks', _iterReplayCallbacks)
    setattr(cls, '__replayPlayMethod', _replayPlayMethod)
    return cls


class BattleReplayPlayersMgr(object):

    def __init__(self):
        self.__knownPlayers = {}

    def addPlayer(self, player):
        playerID = id(player)
        self.__knownPlayers[playerID] = weakref.proxy(player, functools.partial(self.__onPlayerDestroyed, playerID))
        self.__setDataCallbacks(playerID)

    def destroy(self):
        playersIDs = self.__knownPlayers.keys()
        for playerID in playersIDs:
            self.__delDataCallbacks(playerID)
            self.__onPlayerDestroyed(playerID)

    def __setDataCallbacks(self, playerID):
        for name, callback in self.__knownPlayers[playerID].iterReplayCallbacks():
            BattleReplay.g_replayCtrl.setDataCallback(name, callback)

    def __delDataCallbacks(self, playerID):
        for name, callback in self.__knownPlayers[playerID].iterReplayCallbacks():
            BattleReplay.g_replayCtrl.delDataCallback(name, callback)

    def __onPlayerDestroyed(self, playerID, *_):
        del self.__knownPlayers[playerID]
