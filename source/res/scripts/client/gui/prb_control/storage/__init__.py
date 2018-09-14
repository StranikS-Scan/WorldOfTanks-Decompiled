# Embedded file name: scripts/client/gui/prb_control/storage/__init__.py
from constants import PREBATTLE_TYPE as _P_TYPE
from constants import QUEUE_TYPE as _Q_TYPE
from constants import PREBATTLE_TYPE_NAMES as _P_NAMES
from constants import QUEUE_TYPE_NAMES as _Q_NAMES
from gui.prb_control.settings import CTRL_ENTITY_TYPE as _C_TYPE
from gui.prb_control.settings import CTRL_ENTITY_TYPE_NAMES as _C_NAMES
from gui.prb_control.storage.fallout_storage import FalloutLocalStorage
from gui.prb_control.storage.local_storage import LocalStorage
from gui.prb_control.storage.prb_storage import TrainingStorage
from gui.prb_control.storage.sandbox_storage import SandboxStorage
from helpers.ro_property import ROPropertyMeta
__all__ = ('prb_storage_getter', 'prequeue_storage_getter', 'PrbStorageDecorator')

def _makeUniqueName(ctrlName, entityName):
    return '{}_{}'.format(ctrlName, entityName)


def _makePreQueueName(queueType):
    if queueType not in _Q_TYPE.ALL:
        raise ValueError('Queue type is invalid {}'.format(queueType))
    return _makeUniqueName(_C_NAMES[_C_TYPE.PREQUEUE], _Q_NAMES[queueType])


def _makePrbName(prbType):
    if prbType not in _P_TYPE.RANGE:
        raise ValueError('Prebattle type is invalid {}'.format(prbType))
    return _makeUniqueName(_C_NAMES[_C_TYPE.PREBATTLE], _P_NAMES[prbType])


_PRB_STORAGE = {_makePrbName(_P_TYPE.TRAINING): TrainingStorage(),
 _makePreQueueName(_Q_TYPE.EVENT_BATTLES): FalloutLocalStorage(),
 _makePreQueueName(_Q_TYPE.SANDBOX): SandboxStorage()}

class _storage_getter(object):

    def __init__(self, name):
        super(_storage_getter, self).__init__()
        if name not in _PRB_STORAGE:
            raise ValueError('Storage "{}" not found'.format(name))
        self.__name = name

    def __call__(self, *args):
        return _PRB_STORAGE[self.__name]


class prb_storage_getter(_storage_getter):

    def __init__(self, prbType):
        super(prb_storage_getter, self).__init__(_makePrbName(prbType))


class prequeue_storage_getter(_storage_getter):

    def __init__(self, queueType):
        super(prequeue_storage_getter, self).__init__(_makePreQueueName(queueType))


class PrbStorageDecorator(LocalStorage):
    __metaclass__ = ROPropertyMeta
    __readonly__ = _PRB_STORAGE

    def init(self):
        for storage in self.__readonly__.itervalues():
            storage.init()

    def fini(self):
        for storage in self.__readonly__.itervalues():
            storage.fini()

    def swap(self):
        for storage in self.__readonly__.itervalues():
            storage.swap()

    def clear(self):
        for storage in self.__readonly__.itervalues():
            storage.clear()
