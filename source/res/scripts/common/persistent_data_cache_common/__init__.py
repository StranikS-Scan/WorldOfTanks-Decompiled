# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/persistent_data_cache_common/__init__.py
import typing
import wg_async
from persistent_data_cache_common.common import getLogger, DEFAULT_SAVING_TIMEOUT
from persistent_data_cache_common.manager import ForceCreatingPDCManager
from persistent_data_cache_common.serializers import defaultSerializer
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from persistent_data_cache_common.manager import DefaultPDCManager
    from persistent_data_cache_common.types import TData, TDataFactory
    from persistent_data_cache_common.serializers import ISerializer
_logger = getLogger('Manager')
_g_manager = None

def init(mgr):
    global _g_manager
    if _g_manager is not None:
        raise SoftException('PDCManager already initialized.')
    _g_manager = mgr
    return


def load(name, factory, serializer=None):
    if _g_manager is None:
        _logger.debug('Load. Factory for <%s> called directly.', name)
        return factory()
    else:
        return _g_manager.load(name, factory, serializer or defaultSerializer)


def start():
    if _g_manager is None:
        _logger.debug('Start. Not initialized yet.')
        return
    else:
        _g_manager.start()
        return


@wg_async.wg_async
def save(timeout=DEFAULT_SAVING_TIMEOUT):
    if _g_manager is None:
        _logger.debug('Save. Not initialized yet.')
        raise wg_async.AsyncReturn(False)
    yield wg_async.wg_await(_g_manager.save(timeout=timeout))
    return


def fini():
    global _g_manager
    if _g_manager is None:
        _logger.debug('Fini. Not initialized yet.')
        return
    else:
        _g_manager.fini()
        _g_manager = None
        return


def isEnabled():
    return _g_manager is not None
