# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/resources/base.py
import typing
from gui.game_loading import loggers
if typing.TYPE_CHECKING:
    from gui.game_loading.resources.models import BaseResourceModel
_logger = loggers.getResourcesLogger()

class BaseResources(object):
    __slots__ = ()

    def destroy(self, *args, **kwargs):
        self.onDisconnected()
        _logger.debug('%s destroyed.', self)

    def onConnected(self, *args, **kwargs):
        _logger.debug('%s on connected called.', self)

    def onDisconnected(self, *args, **kwargs):
        _logger.debug('%s on disconnected called.', self)

    def reset(self, *args, **kwargs):
        _logger.debug('%s restarted.', self)

    def get(self, *args, **kwargs):
        raise NotImplementedError

    def __repr__(self):
        return '<Resources:{}>'.format(self.__class__.__name__)
