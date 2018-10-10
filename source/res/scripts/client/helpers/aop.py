# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/aop.py
import re
import sys
import types
import weakref
from functools import partial
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_DEBUG

def copy(wrapper, wrapped):
    if hasattr(wrapped, '__module__'):
        setattr(wrapper, '__module__', wrapped.__module__)
    if hasattr(wrapped, 'im_class'):
        setattr(wrapper, 'im_class', wrapped.im_self)
    setattr(wrapper, '__name__', wrapped.__name__)
    setattr(wrapper, '__doc__', wrapped.__doc__)


def execFunction(wrapped, args, kwargs):
    func = wrapped.__original__
    cd = CallData(wrapped, func, args, kwargs)
    count = 0
    tb = None
    aspectList = wrapped.__aspects__
    for aspect in aspectList:
        try:
            ret = aspect.atCall(cd)
            if cd._change:
                cd._args, cd._kwargs = ret
                cd._change = False
            elif cd._avoid:
                cd._returned = ret
                break
        except BaseException as e:
            tb = sys.exc_info()[2]
            if cd._avoid:
                cd._exception = e
                break
            else:
                raise

        count += 1

    if not cd._avoid:
        try:
            cd._returned = func(*cd._packArgs(), **cd._kwargs)
        except BaseException as e:
            cd._exception = e
            tb = sys.exc_info()[2]

    aspectList = aspectList[:count]
    aspectList.reverse()
    for aspect in aspectList:
        try:
            if cd._exception:
                ret = aspect.atRaise(cd)
            else:
                ret = aspect.atReturn(cd)
            if cd._change:
                cd._returned = ret
                cd._exception = None
                cd._change = False
        except BaseException as e:
            tb = sys.exc_info()[2]
            if cd._change:
                cd._returned = None
                cd._exception = e
                cd._change = False
            else:
                raise

    if cd._exception:
        raise cd._exception.__class__, cd._exception, tb
    return cd._returned


def wrap(func):
    if getattr(func, '__aspects__', None) is not None:
        return func
    else:

        def _make():

            def _wrapper(*args, **kwargs):
                return execFunction(_getter(), args, kwargs)

            _getter = weakref.ref(_wrapper)
            return _wrapper

        wrapper = _make()
        copy(wrapper, func)
        wrapper.__aspects__ = []
        wrapper.__original__ = func
        wrapper.__ismethod__ = None
        return wrapper


def pointcutable(pointcutTag=None):
    if callable(pointcutTag):
        return _addPointcutableTag(func=pointcutTag)
    else:
        return partial(_addPointcutableTag, tag=pointcutTag) if pointcutTag is not None else _addPointcutableTag


def _addPointcutableTag(func, tag=None):
    setattr(func, '__pointcutable__', tag)
    return func


def _restore(ns, wrapper):
    aspects = getattr(wrapper, '__aspects__', [])
    while aspects:
        aspects.pop().clear()

    if hasattr(wrapper, '__original__'):
        setattr(ns, wrapper.__name__, wrapper.__original__)


def _regexpCriteria(func, regexp, match):
    if regexp.match(func.__name__):
        if match:
            return True
    elif not match:
        return True
    return False


def _pointcutableCriteria(func, pointcutTag):
    return func.__pointcutable__ == pointcutTag if hasattr(func, '__pointcutable__') else False


def _isearch(ns, criteria):
    for attrName in dir(ns):
        attr = getattr(ns, attrName)
        if isinstance(attr, (types.FunctionType, types.MethodType)) and criteria(attr):
            yield attrName


def _hasWrappedMethod(clazz, function):
    attr = getattr(clazz, function.__name__, None)
    originalFunc = getattr(attr, '__original__', None)
    if originalFunc is function:
        return True
    else:
        for baseClass in clazz.__bases__:
            if _hasWrappedMethod(baseClass, function):
                return True

        return False


class CallData(object):

    def __init__(self, wrapped, function, args, kwargs):
        self._function = function
        self._kwargs = kwargs
        self._returned = None
        self._exception = None
        if wrapped.__ismethod__ is None:
            try:
                clazz = args[0].__class__
                wrapped.__ismethod__ = _hasWrappedMethod(clazz, function)
            except BaseException:
                wrapped.__ismethod__ = False

        if wrapped.__ismethod__:
            slf = args[0]
            args = args[1:]
            cls = slf.__class__
        else:
            slf = None
            cls = None
        self._self = slf
        self._cls = cls
        self._args = args
        self._avoid = False
        self._change = False
        return

    @property
    def function(self):
        return self._function

    @property
    def cls(self):
        return self._cls

    @property
    def self(self):
        return self._self

    @property
    def args(self):
        return tuple(self._args)

    @property
    def kwargs(self):
        return self._kwargs.copy()

    def findArg(self, argIndex, argName):
        return self._args[argIndex] if len(self._args) > argIndex else self._kwargs.get(argName, None)

    def changeArgs(self, *changes):
        if changes:
            newArgs, newKwargs = list(self.args), self.kwargs
            for argIndex, argName, newValue in changes:
                if len(self._args) > argIndex:
                    newArgs[argIndex] = newValue
                newKwargs[argName] = newValue

            self.change()
            return (newArgs, newKwargs)
        return (self.args, self.kwargs)

    @property
    def returned(self):
        return self._returned

    @property
    def exception(self):
        return self._exception

    def _packArgs(self):
        return self._args if self._self is None else (self._self,) + tuple(self._args)

    def exceptionIs(self, cls):
        return False if self._exception is None else isinstance(self._exception, cls)

    def avoid(self):
        self._avoid = True

    def change(self):
        self._change = True


class Aspect(object):

    def __del__(self):
        LOG_DEBUG('Aspect deleted: {0:>s}'.format(self))

    def __call__(self, func):
        wrapped = wrap(func)
        if hasattr(wrapped, '__aspects__'):
            wrapped.__aspects__.insert(0, self)
        else:
            LOG_ERROR('Function is not wrapper', self)
        return wrapped

    def atCall(self, cd):
        pass

    def atRaise(self, cd):
        pass

    def atReturn(self, cd):
        pass

    def clear(self):
        pass


class DummyAspect(Aspect):

    def atCall(self, cd):
        cd.avoid()


AspectType = type(Aspect)

class Pointcut(list):

    def __del__(self):
        LOG_DEBUG('Pointcut deleted: {0:>s}'.format(self))

    def __init__(self, path, name, filterString=None, pointcutTag=None, match=True, aspects=()):
        super(Pointcut, self).__init__()
        self.__nsPath = path
        self.__nsName = name
        ns = self.getNs(path, name)
        if ns is None:
            return
        else:
            if filterString is not None:
                criteria = partial(_regexpCriteria, regexp=re.compile(filterString), match=match)
            else:
                criteria = partial(_pointcutableCriteria, pointcutTag=pointcutTag)
            for item in _isearch(ns, criteria):
                wrapped = wrap(getattr(ns, item))
                setattr(ns, item, wrapped)
                self.append(wrapped)

            for aspect in aspects:
                self.addAspect(aspect)

            return

    def getNs(self, path, name):
        imported = __import__(path, globals(), locals(), [name])
        return getattr(imported, name, None)

    def addAspect(self, aspect, *args, **kwargs):
        if isinstance(aspect, AspectType):
            for item in self:
                aspect(*args, **kwargs)(item)

        else:
            for item in self:
                aspect(item)

    def clear(self):
        ns = self.getNs(self.__nsPath, self.__nsName)
        if ns is None:
            return
        else:
            for item in self:
                _restore(ns, item)

            return


PointcutType = type(Pointcut)

class Weaver(object):
    __slots__ = ('__pointcuts',)

    def __init__(self):
        self.__pointcuts = []

    def weave(self, *args, **kwargs):
        pointcut = kwargs.pop('pointcut', Pointcut)
        aspects = kwargs.pop('aspects', ())
        avoid = kwargs.pop('avoid', False)
        if isinstance(pointcut, PointcutType):
            try:
                pointcut = pointcut(*args, **kwargs)
            except ImportError:
                LOG_CURRENT_EXCEPTION()
                return -1

        result = len(self.__pointcuts)
        if avoid:
            aspects = (DummyAspect,)
        for aspect in aspects:
            try:
                pointcut.addAspect(aspect)
            except TypeError:
                LOG_CURRENT_EXCEPTION()

        self.__pointcuts.append(pointcut)
        return result

    def addAspect(self, idx, aspect, *args, **kwargs):
        if -1 < idx < len(self.__pointcuts):
            pointcut = self.__pointcuts[idx]
            try:
                pointcut.addAspect(aspect, *args, **kwargs)
            except TypeError:
                LOG_CURRENT_EXCEPTION()

    def findPointcut(self, pointcut):
        if isinstance(pointcut, PointcutType):
            clazz = pointcut
        else:
            clazz = pointcut.__class__
        for idx, item in enumerate(self.__pointcuts):
            if item.__class__ == clazz:
                return idx

    def avoid(self, idx):
        self.addAspect(idx, DummyAspect)

    def clear(self, idx=None):
        if idx is not None:
            if -1 < idx < len(self.__pointcuts):
                pointcut = self.__pointcuts.pop(idx)
                pointcut.clear()
        else:
            pointcuts = self.__pointcuts
            while pointcuts:
                pointcuts.pop().clear()

        return
