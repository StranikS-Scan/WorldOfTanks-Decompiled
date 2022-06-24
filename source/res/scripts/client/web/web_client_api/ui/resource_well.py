# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/resource_well.py
import logging
from gui.shared.event_dispatcher import showShop, showHangar
from helpers import dependency
from skeletons.gui.game_control import IResourceWellController
from uilogging.resource_well.loggers import ResourceWellEntryPointLogger
from web.web_client_api import w2c, W2CSchema, Field
from gui.shared import event_dispatcher as shared_events
_logger = logging.getLogger(__name__)

class _ResourceWellTabSchema(W2CSchema):
    back_to_shop = Field(required=False, type=bool, default=True)


class ResourceWellWebApiMixin(object):
    __resourceWell = dependency.descriptor(IResourceWellController)

    @w2c(_ResourceWellTabSchema, 'resource_well')
    def showResourceWell(self, cmd):
        if self.__resourceWell.isActive():
            backToShop = cmd.back_to_shop
            ResourceWellEntryPointLogger().logWebClick(backToShop=backToShop)
            shared_events.showResourceWellProgressionWindow(backCallback=showShop if backToShop else showHangar)
        else:
            _logger.error('Resource Well is not active at the moment!')
