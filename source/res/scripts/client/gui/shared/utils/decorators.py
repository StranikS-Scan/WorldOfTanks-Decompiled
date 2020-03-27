# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/decorators.py
import time
from string import join
import adisp
import BigWorld
from debug_utils import LOG_DEBUG
from gui.Scaleform.Waiting import Waiting

class process(object):

    def __init__(self, *kargs):
        self.__currentMessage = None
        self.__messages = kargs
        self.__messages2Show = list(self.__messages)
        return

    def __hideWaiting(self):
        if self.__currentMessage is not None:
            Waiting.hide(self.__currentMessage)
            self.__currentMessage = None
        return

    def __nextWaiting(self):
        if self.__messages2Show:
            self.__hideWaiting()
            self.__currentMessage = self.__messages2Show.pop(0)
            Waiting.show(self.__currentMessage)

    def __stepCallback(self, isStop):
        if not isStop:
            return self.__nextWaiting()
        self.__hideWaiting()
        self.__messages2Show = list(self.__messages)

    def __call__(self, func):

        def wrapper(*kargs, **kwargs):
            self.__nextWaiting()
            return adisp.process(func, self.__stepCallback)(*kargs, **kwargs)

        return wrapper


def async(func, cbname='callback', cbwrapper=lambda x: x):

    def wrapper(*kargs, **kwargs):
        if cbname in func.func_code.co_varnames:
            idx = func.func_code.co_varnames.index(cbname)
            if idx >= len(kargs) and cbname not in kwargs:
                return adisp.async(func, cbname, cbwrapper)(*kargs, **kwargs)
        return func(*kargs, **kwargs)

    return wrapper


def debugTime(func):

    def wrapper(*args, **kwargs):
        startTime = time.time()
        result = func(*args, **kwargs)
        LOG_DEBUG("Method '%s' measuring time: %.10f" % (func.__name__, time.time() - startTime))
        return result

    return wrapper


IS_DEVELOPMENT = True

class _TrackFrameEnabled(object):

    def __init__(self, logID):
        super(_TrackFrameEnabled, self).__init__()
        self.__logID = logID

    def __call__(self, func):

        def wrapper(*args, **kwargs):
            BigWorld.PFbeginFrame(self.__logID)
            func(*args, **kwargs)
            BigWorld.PFendFrame()

        return wrapper


class _TrackFrameDisabled(object):

    def __init__(self, logID):
        super(_TrackFrameDisabled, self).__init__()

    def __call__(self, func):
        return func


if IS_DEVELOPMENT:
    trackFrame = _TrackFrameEnabled
else:
    trackFrame = _TrackFrameDisabled

def makeArr(obj):
    if isinstance(obj, tuple):
        if len(obj) > 1:
            return [obj[0], obj[1]]
        return [obj[0], obj[0]]
    return [obj, obj]


class ReprInjector(object):

    @classmethod
    def withParent(cls, *argNames):
        return InternalRepresenter(True, argNames)

    @classmethod
    def simple(cls, *argNames):
        return InternalRepresenter(False, argNames)


class InternalRepresenter(object):

    def __init__(self, reprParentFlag, argNames):
        self.argNames = argNames
        self.reprParentFlag = reprParentFlag

    def __call__(self, clazz):
        if '__repr__' in dir(clazz):
            if hasattr(clazz, '__repr_params__') and self.reprParentFlag is not False:
                clazz.__repr_params__ = tuple((arg for arg in self.argNames if arg not in clazz.__repr_params__)) + tuple((arg for arg in clazz.__repr_params__ if arg[0:2] != '__'))
            else:
                clazz.__repr_params__ = self.argNames
        else:
            clazz.__repr_params__ = self.argNames
        representation = []
        attrMethNames = []
        for i in xrange(len(clazz.__repr_params__)):
            attrMethNames.append(makeArr(clazz.__repr_params__[i]))
            if attrMethNames[-1][0][:2] == '__':
                if clazz.__name__[0] != '_':
                    attrMethNames[-1][0] = join(['_', clazz.__name__, attrMethNames[-1][0]], sep='')
                else:
                    attrMethNames[-1][0] = join([clazz.__name__, attrMethNames[-1][0]], sep='')
            representation.append('{0} = {{{1}}}'.format(attrMethNames[-1][1], i))

        representation = join([clazz.__name__,
         '(',
         join(representation, sep=', '),
         ')'], sep='')

        def __repr__(self):
            formatedArgs = []
            for attrMethName, _ in attrMethNames:
                attr = getattr(self, attrMethName, 'N/A')
                if callable(attr):
                    attr = getattr(self, attrMethName, 'N/A')()
                formatedArgs.append(attr)

            return representation.format(*formatedArgs)

        clazz.__repr__ = __repr__
        return clazz
