# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gui_decorators.py
import functools
import inspect
import logging
from frameworks.wulf import View, ViewStatus
from helpers.uniprof import regions
_REGION_FORMAT = 'view.{}.{}'
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

def trackLifeCycle(uniqueName):
    return ViewLifeCycleToRegions(uniqueName)


class ViewLifeCycleToRegions(object):
    __slots__ = ('__uniqueName', '__viewStatus')

    def __init__(self, uniqueName):
        super(ViewLifeCycleToRegions, self).__init__()
        self.__uniqueName = uniqueName
        self.__viewStatus = ViewStatus.UNDEFINED

    def __call__(self, clazz):
        if View not in inspect.getmro(clazz):
            raise UserWarning('The following argument {} is not subclass of View'.format(clazz))

        def swap(func):

            @functools.wraps(func)
            def wrapper(view, oldStatus, newStatus, *args, **kwargs):
                func(view, oldStatus, newStatus, *args, **kwargs)
                self.__trigger(newStatus)

            return wrapper

        if not getattr(clazz, '__lifeCycleTracked__', False):
            setattr(clazz, '_swapStates', swap(getattr(clazz, '_swapStates')))
            setattr(clazz, '__lifeCycleTracked__', True)
        else:
            _logger.warning('Class already wrapped: %r', clazz)
        return clazz

    def __enter(self):
        regions.enterToRegion(_REGION_FORMAT.format(self.__uniqueName, ViewStatus.getKeyByValue(self.__viewStatus).lower()))

    def __exit(self):
        regions.exitFromRegion(_REGION_FORMAT.format(self.__uniqueName, ViewStatus.getKeyByValue(self.__viewStatus).lower()))

    def __trigger(self, newState):
        if self.__viewStatus != ViewStatus.UNDEFINED:
            self.__exit()
        self.__viewStatus = newState
        if self.__viewStatus != ViewStatus.DESTROYED:
            self.__enter()
