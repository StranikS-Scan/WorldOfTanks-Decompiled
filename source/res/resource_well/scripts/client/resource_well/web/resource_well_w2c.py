# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/web/resource_well_w2c.py
from __future__ import absolute_import
import logging
from helpers import dependency
from resource_well.gui.shared.event_dispatcher import showMainWindow
from skeletons.gui.resource_well import IResourceWellController
from web.web_client_api.ui import OpenTabWebApi
_logger = logging.getLogger(__name__)

def registerResourceWellOpenTabWebApi():

    @dependency.replace_none_kwargs(resourceWell=IResourceWellController)
    def _showResourceWell(_, cmd, resourceWell=None):
        if resourceWell.isActive():
            showMainWindow()
        else:
            _logger.error('Resource Well is not active at the moment!')

    OpenTabWebApi.addTabIdCallback('resource_well', _showResourceWell)
    return
